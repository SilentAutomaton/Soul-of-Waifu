import os
import sys
import json
import shutil
import tarfile
import zipfile
import asyncio
import aiohttp
import logging
from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger("LlamaUpdater")

class LlamaUpdater(QtCore.QObject):
    progress_signal = QtCore.pyqtSignal(int, str)
    finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, backend_dir: Path):
        super().__init__()
        self.backend_dir = backend_dir
        self.cache_dir = backend_dir / "_update_cache"
        self.backup_dir = backend_dir / "_backup"
        self.version_file = backend_dir / "version.json"
        self.github_api_url = "https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=10"

    async def fetch_latest_release(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.github_api_url, timeout=10) as response:
                    if response.status != 200:
                        return None, f"GitHub API error: HTTP {response.status}"
                    data = await response.json()
                    # "releases/latest" can point to a release without binaries (e.g. a bindings tag),
                    # so pick the newest release that actually ships prebuilt builds.
                    for release in data:
                        if any("-bin-" in asset.get("name", "") for asset in release.get("assets", [])):
                            return release, None
                    return None, "No llama.cpp release with prebuilt binaries found"
        except Exception as e:
            return None, str(e)

    def _get_current_version(self, backend_type: str) -> str:
        if self.version_file.exists():
            try:
                data = json.loads(self.version_file.read_text())
                return data.get(backend_type.lower(), "unknown")
            except Exception:
                pass
        return "unknown"

    def _match_assets(self, assets: list, backend_type: str) -> list:
        if sys.platform != "win32":
            return self._match_linux_assets(assets, backend_type)

        matched_urls = []
        backend_type = backend_type.lower()
        
        def matches(name, keywords):
            return all(kw in name for kw in keywords) and "arm64" not in name

        for asset in assets:
            name = asset.get("name", "").lower()
            if asset.get("content_type") not in ["application/zip", "application/x-zip-compressed"] and not name.endswith(".zip"):
                continue

            if backend_type == "cpu" and matches(name, ["llama", "win", "cpu", "x64"]):
                matched_urls.append(asset["browser_download_url"])
            
            elif backend_type == "cuda":
                if matches(name, ["llama", "win", "cuda", "12", "x64"]):
                    matched_urls.append(asset["browser_download_url"])
                elif matches(name, ["cudart", "win", "cuda", "12", "x64"]):
                    matched_urls.append(asset["browser_download_url"])
            
            elif backend_type == "vulkan" and matches(name, ["llama", "win", "vulkan", "x64"]):
                matched_urls.append(asset["browser_download_url"])
            
            elif backend_type == "hip" and matches(name, ["llama", "win", "hip", "radeon", "x64"]):
                matched_urls.append(asset["browser_download_url"])
            
            elif backend_type == "sycl" and matches(name, ["llama", "win", "sycl", "x64"]):
                matched_urls.append(asset["browser_download_url"])
                
        return matched_urls

    @staticmethod
    def _match_linux_assets(assets: list, backend_type: str) -> list:
        """
        Pick the official Ubuntu x64 build (works on most distros) for the backend.
        llama.cpp publishes no Linux CUDA binaries - use a system llama-server
        (e.g. the AUR package llama.cpp-cuda) or the Vulkan backend instead.
        """
        backend_type = backend_type.lower()
        keywords = {
            "cpu": ["ubuntu", "x64"],
            "vulkan": ["ubuntu", "vulkan", "x64"],
            "hip": ["ubuntu", "rocm", "x64"],
            "sycl": ["ubuntu", "sycl", "fp16", "x64"],
        }.get(backend_type)
        if not keywords:
            return []

        variants = ("vulkan", "rocm", "hip", "sycl", "openvino", "cuda", "s390x")
        for asset in assets:
            name = asset.get("name", "").lower()
            if not name.startswith("llama-") or not name.endswith((".tar.gz", ".zip")) or "arm64" in name:
                continue
            if not all(kw in name for kw in keywords):
                continue
            if backend_type == "cpu" and any(v in name for v in variants):
                continue
            return [asset["browser_download_url"]]
        return []

    @staticmethod
    def _extract_zip(archive_path: Path, target_folder: Path):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(('.exe', '.dll')):
                    filename = Path(file_info.filename).name
                    extracted_path = target_folder / filename

                    if extracted_path.exists():
                        os.remove(extracted_path)

                    with zip_ref.open(file_info) as source, open(extracted_path, "wb") as target:
                        shutil.copyfileobj(source, target)

    @staticmethod
    def _extract_tarball(archive_path: Path, target_folder: Path):
        """Flatten the llama.cpp Linux tarball: executables + shared libraries into target_folder."""
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                name = Path(member.name).name
                is_lib = ".so" in name
                is_bin = name.startswith(("llama-", "rpc-"))
                if not name or not (is_lib or is_bin) or not (member.isfile() or member.issym()):
                    continue

                dest = target_folder / name
                if dest.is_symlink() or dest.exists():
                    dest.unlink()

                if member.issym():
                    # Only keep links that point into the same folder (libfoo.so -> libfoo.so.0).
                    os.symlink(Path(member.linkname).name, dest)
                    continue

                with tar.extractfile(member) as source, open(dest, "wb") as target:
                    shutil.copyfileobj(source, target)
                os.chmod(dest, 0o755 if (is_bin or member.mode & 0o111) else 0o644)

    async def download_and_install(self, asset_urls: list, backend_type: str, version_tag: str):
        target_folder = self.backend_dir / backend_type.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._create_backup(target_folder)
        target_folder.mkdir(parents=True, exist_ok=True)

        try:
            for idx, url in enumerate(asset_urls):
                archive_ext = ".tar.gz" if url.lower().endswith(".tar.gz") else ".zip"
                zip_path = self.cache_dir / f"update_{idx}{archive_ext}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download file from {url}")

                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        with open(zip_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size:
                                    percent = int((downloaded / total_size) * 100)
                                    self.progress_signal.emit(percent, f"Downloading part [{idx+1}/{len(asset_urls)}]... {downloaded//1024//1024}MB / {total_size//1024//1024}MB")

                self.progress_signal.emit(100, f"Extracting part [{idx+1}/{len(asset_urls)}]...")
                await asyncio.sleep(0.5)

                if archive_ext == ".tar.gz":
                    self._extract_tarball(zip_path, target_folder)
                else:
                    self._extract_zip(zip_path, target_folder)

                if zip_path.exists():
                    os.remove(zip_path)

            ver_data = {}
            if self.version_file.exists():
                try:
                    ver_data = json.loads(self.version_file.read_text())
                except Exception:
                    pass
            
            ver_data[backend_type.lower()] = version_tag
            
            self.version_file.write_text(json.dumps(ver_data, indent=4))
            
            self.finished_signal.emit(True, f"Successfully updated {backend_type.upper()} engine to {version_tag}!")

        except PermissionError:
            self.finished_signal.emit(False, "Permission Denied! Ensure the LLM server is STOPPED.")
            await self.restore_backup(backend_type)
        except Exception as e:
            self.finished_signal.emit(False, f"Update error: {e}")
            await self.restore_backup(backend_type)

    def _create_backup(self, target_folder: Path):
        if not target_folder.exists():
            return
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_folder = self.backup_dir / target_folder.name
        
        if backup_folder.exists():
            shutil.rmtree(backup_folder)
        
        shutil.copytree(target_folder, backup_folder)
        logger.info(f"Backup created for {target_folder.name}")

    async def restore_backup(self, backend_type: str):
        target_folder = self.backend_dir / backend_type.lower()
        backup_folder = self.backup_dir / backend_type.lower()
        
        if not backup_folder.exists():
            return False, "No backup found for this backend."

        try:
            if target_folder.exists():
                shutil.rmtree(target_folder)
            shutil.copytree(backup_folder, target_folder)
            return True, "Successfully reverted to the previous version!"
        except Exception as e:
            return False, f"Failed to restore backup: {e}"
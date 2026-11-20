"""
Bing API 服务
"""
import httpx
from typing import Optional
from datetime import date
from loguru import logger
from app.config import settings


class BingService:
    """Bing API 服务"""
    
    def __init__(self):
        self.base_url = settings.BING_API_BASE
        self.timeout = httpx.Timeout(30.0, connect=10.0)
    
    async def get_random_uhd_url(self) -> str:
        """获取随机 4K 壁纸 URL"""
        url = f"{self.base_url}/rand_uhd.php"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                return str(response.url)
            except Exception as e:
                logger.error(f"获取随机壁纸 URL 失败: {e}")
                raise
    
    async def get_today_uhd_url(self) -> str:
        """获取今日 4K 壁纸 URL"""
        url = f"{self.base_url}/uhd.php"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                return str(response.url)
            except Exception as e:
                logger.error(f"获取今日壁纸 URL 失败: {e}")
                raise
    
    async def get_random_1080p_url(self) -> str:
        """获取随机 1080P 壁纸 URL"""
        url = f"{self.base_url}/rand.php"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                return str(response.url)
            except Exception as e:
                logger.error(f"获取随机 1080P 壁纸 URL 失败: {e}")
                raise
    
    async def download_image(self, image_url: str, save_path: str) -> bool:
        """下载图片到本地"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(image_url)
                response.raise_for_status()
                
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"图片下载成功: {save_path}")
                return True
            except Exception as e:
                logger.error(f"下载图片失败: {e}")
                raise
    
    async def get_image_info(self, image_url: str) -> dict:
        """获取图片信息（从 URL 解析）"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.head(image_url)
                content_length = response.headers.get("content-length", "0")
                content_type = response.headers.get("content-type", "image/jpeg")
                
                return {
                    "url": image_url,
                    "size": int(content_length),
                    "type": content_type,
                }
        except Exception as e:
            logger.warning(f"获取图片信息失败: {e}")
            return {"url": image_url, "size": 0, "type": "unknown"}


bing_service = BingService()

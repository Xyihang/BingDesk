"""
Windows 壁纸设置工具
"""
import ctypes
import os
from loguru import logger


def set_wallpaper(image_path: str) -> bool:
    """
    设置 Windows 桌面壁纸
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"壁纸文件不存在: {image_path}")
            return False
        
        abs_path = os.path.abspath(image_path)
        
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02
        
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE,
        )
        
        if result:
            logger.info(f"壁纸设置成功: {abs_path}")
            return True
        else:
            logger.error("壁纸设置失败: SystemParametersInfoW 返回 0")
            return False
            
    except Exception as e:
        logger.error(f"设置壁纸时发生错误: {e}")
        return False


def get_wallpaper() -> str:
    """
    获取当前桌面壁纸路径
    
    Returns:
        str: 当前壁纸路径
    """
    try:
        SPI_GETDESKWALLPAPER = 0x73
        MAX_PATH = 260
        
        buffer = ctypes.create_unicode_buffer(MAX_PATH)
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETDESKWALLPAPER,
            MAX_PATH,
            buffer,
            0,
        )
        
        return buffer.value
        
    except Exception as e:
        logger.error(f"获取壁纸路径失败: {e}")
        return ""

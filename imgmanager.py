import requests
import mimetypes
import io

def get_image(url: str) -> tuple[str, str] | tuple[str, None]:
    ''' 尝试从 url 获取图片 '''
    header = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers = header)
        response.raise_for_status()
        image_type = response.headers.get('Content-Type', None)

        if not image_type:
            extension = url.split('.')[-1]
            image_type = mimetypes.types_map.get(f'.{extension}', 'application/octet-stream')

        image_data = io.BytesIO(response.content)

    except Exception as e:
        return str(e), None
    
    return image_data, image_type
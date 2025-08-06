# 前后端对接所需的后端接口

## 1. 数据下载接口
```python
# 在 main_app/views.py 中添加
from django.http import HttpResponse, FileResponse
import os
import zipfile
import tempfile
import json

@login_required
def download_data(request):
    """数据下载接口"""
    if request.method == 'POST':
        # 获取前端参数
        data_category = request.POST.get('category')  # 数据类别
        pollutant_type = request.POST.get('pollutant')  # 污染物类型
        time_range = request.POST.get('time_range')  # 时间范围类型
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # 根据参数生成数据文件
        # 这里需要你的搭档实现具体的数据生成逻辑
        
        # 返回文件下载
        response = FileResponse(...)
        response['Content-Disposition'] = f'attachment; filename="data_{data_category}_{pollutant_type}.csv"'
        return response
    
    return JsonResponse({'error': '请求方法错误'}, status=405)

@login_required  
def export_data(request):
    """数据导出接口（JSON格式）"""
    # 类似的导出逻辑
    pass
```

## 2. 数据预览接口
```python
@login_required
def preview_data(request):
    """数据预览接口"""
    if request.method == 'POST':
        # 获取参数并返回预览数据
        data = {
            'preview': [...],  # 预览数据
            'total_count': 1000,  # 总数据量
            'columns': [...],  # 数据列信息
        }
        return JsonResponse(data)
```

## 3. 数据统计接口
```python
@login_required
def data_statistics(request):
    """获取数据统计信息"""
    stats = {
        'total_records': 50000,
        'date_range': ['2015-01-01', '2023-12-31'],
        'available_pollutants': ['PM2.5', 'PM10', 'NO2', 'O3'],
        'available_regions': ['北京', '上海', '广州', ...]
    }
    return JsonResponse(stats)
```

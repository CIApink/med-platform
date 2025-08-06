# 简化测试版本 - 可以立即测试前后端连接

# 将以下代码添加到 main_app/views.py 文件的末尾用于测试

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import csv
import io
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def download_data(request):
    """临时测试版本的数据下载接口"""
    try:
        # 获取参数
        category = request.POST.get('category', '未知类别')
        pollutant = request.POST.get('pollutant', '未知污染物')
        time_range = request.POST.get('time_range', '未知时间范围')
        start_date = request.POST.get('start_date', '未知开始时间')
        end_date = request.POST.get('end_date', '未知结束时间')
        
        # 创建测试CSV数据
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="test_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # 添加BOM以支持中文
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # 写入表头
        writer.writerow(['参数名称', '参数值'])
        writer.writerow(['数据类别', category])
        writer.writerow(['污染物类型', pollutant])
        writer.writerow(['时间范围', time_range])
        writer.writerow(['开始时间', start_date])
        writer.writerow(['结束时间', end_date])
        writer.writerow(['用户', request.user.email])
        writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        # 写入一些测试数据
        writer.writerow([])  # 空行
        writer.writerow(['测试数据'])
        writer.writerow(['日期', '城市', 'PM2.5', 'PM10', 'AQI'])
        
        # 生成几行示例数据
        import random
        cities = ['北京', '上海', '广州', '深圳', '杭州']
        for i in range(10):
            date = f'2023-{(i%12)+1:02d}'
            city = cities[i % len(cities)]
            pm25 = random.randint(20, 150)
            pm10 = random.randint(30, 200)
            aqi = random.randint(50, 300)
            writer.writerow([date, city, pm25, pm10, aqi])
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'下载失败: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"]) 
def export_data(request):
    """临时测试版本的数据导出接口"""
    try:
        category = request.POST.get('category', '未知类别')
        pollutant = request.POST.get('pollutant', '未知污染物')
        
        test_data = {
            'message': '这是测试导出功能',
            'parameters': {
                'category': category,
                'pollutant': pollutant,
                'user': request.user.email,
                'export_time': datetime.now().isoformat()
            },
            'sample_data': [
                {'date': '2023-01', 'city': '北京', 'pm25': 45},
                {'date': '2023-01', 'city': '上海', 'pm25': 38},
                {'date': '2023-01', 'city': '广州', 'pm25': 42}
            ]
        }
        
        import json
        response = HttpResponse(
            json.dumps(test_data, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="test_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'导出失败: {str(e)}'}, status=500)

@login_required
def preview_data(request):
    """测试版本的数据预览接口"""
    return JsonResponse({
        'message': '预览功能测试成功',
        'preview': [
            ['2023-01', '北京', 45, 78, 89],
            ['2023-01', '上海', 38, 65, 76],
            ['2023-01', '广州', 42, 70, 82]
        ],
        'total_count': 100,
        'columns': ['日期', '城市', 'PM2.5', 'PM10', 'AQI']
    })

@login_required
def data_statistics(request):
    """测试版本的数据统计接口"""
    return JsonResponse({
        'message': '统计功能测试成功',
        'total_records': 12500,
        'available_data': ['PM2.5', 'PM10', 'NO2', 'O3'],
        'date_range': ['2015-01-01', '2023-12-31'],
        'last_updated': datetime.now().isoformat()
    })

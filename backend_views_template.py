# 这是你的搭档需要在 main_app/views.py 文件末尾添加的代码

from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import AuditLog  # 确保导入AuditLog模型
import csv
import io
import json
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def download_data(request):
    """数据下载接口"""
    try:
        # 获取前端传来的参数
        category = request.POST.get('category', 'CN environmental data')
        pollutant = request.POST.get('pollutant', 'PM2.5')
        time_range = request.POST.get('time_range', 'month')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # 记录下载日志（可选）
        AuditLog.objects.create(
            user=request.user,
            action='data_download',
            details=f'下载 {category} - {pollutant} 数据，时间范围：{start_date} 到 {end_date}',
            ip_address=request.META.get('REMOTE_ADDR'),
            timestamp=timezone.now()
        )
        
        # 这里你的搭档需要实现具体的数据查询和生成逻辑
        # 示例代码：
        data = generate_sample_data(category, pollutant, time_range, start_date, end_date)
        
        # 创建CSV文件
        response = HttpResponse(content_type='text/csv')
        filename = f'env_data_{pollutant}_{start_date}_to_{end_date}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # 写入CSV数据
        writer = csv.writer(response)
        
        # 写入表头
        if category == 'CN environmental data':
            if '气象' in pollutant:
                writer.writerow(['日期', '城市', '温度(°C)', '湿度(%)', '紫外辐射强度'])
            elif '建城' in pollutant:
                writer.writerow(['日期', '城市', 'NDVI', '夜光数据'])
            else:  # 大气污染数据
                writer.writerow(['日期', '城市', 'PM2.5', 'PM10', 'NO2', 'O3', 'AQI'])
        else:  # 英国数据
            writer.writerow(['Date', 'City', 'PM2.5', 'PM10', 'NO2', 'O3', 'AQI'])
        
        # 写入数据行
        for row in data:
            writer.writerow(row)
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required 
@require_http_methods(["POST"])
def export_data(request):
    """数据导出接口（JSON格式）"""
    try:
        # 获取参数
        category = request.POST.get('category', 'CN environmental data')
        pollutant = request.POST.get('pollutant', 'PM2.5')
        time_range = request.POST.get('time_range', 'month')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # 生成数据
        data = generate_sample_data(category, pollutant, time_range, start_date, end_date)
        
        # 转换为JSON格式
        json_data = {
            'metadata': {
                'category': category,
                'pollutant': pollutant,
                'time_range': time_range,
                'start_date': start_date,
                'end_date': end_date,
                'export_time': datetime.now().isoformat(),
                'total_records': len(data)
            },
            'data': data
        }
        
        # 返回JSON文件下载
        response = HttpResponse(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
        filename = f'env_data_{pollutant}_{start_date}_to_{end_date}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def preview_data(request):
    """数据预览接口"""
    try:
        category = request.POST.get('category', 'CN environmental data')
        pollutant = request.POST.get('pollutant', 'PM2.5')
        time_range = request.POST.get('time_range', 'month')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # 生成预览数据（只返回前10条）
        all_data = generate_sample_data(category, pollutant, time_range, start_date, end_date)
        preview_data = all_data[:10]  # 只取前10条作为预览
        
        return JsonResponse({
            'preview': preview_data,
            'total_count': len(all_data),
            'columns': get_column_info(category, pollutant),
            'metadata': {
                'category': category,
                'pollutant': pollutant,
                'time_range': time_range,
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def data_statistics(request):
    """获取数据统计信息"""
    try:
        # 这里你的搭档需要从数据库或数据文件中获取真实的统计信息
        stats = {
            'total_records': 125000,
            'date_range': {
                'start': '2015-01-01',
                'end': '2023-12-31'
            },
            'available_categories': {
                'CN environmental data': {
                    'air_pollution': ['PM2.5', 'PM2.5-PM10', 'PM10', 'NO2', 'O3'],
                    'weather': ['温度', '紫外辐射'],
                    'urban': ['NDVI', '夜光数据']
                },
                'UK environmental data': {
                    'air_pollution': ['PM2.5', 'PM10', 'NO2', 'O3']
                }
            },
            'available_regions': {
                'china': ['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆'],
                'uk': ['London', 'Manchester', 'Birmingham', 'Edinburgh']
            },
            'data_formats': ['CSV', 'JSON'],
            'time_ranges': ['年均', '月均'],
            'last_updated': '2023-12-31'
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 辅助函数
def generate_sample_data(category, pollutant, time_range, start_date, end_date):
    """
    生成示例数据 - 你的搭档需要替换为真实的数据查询逻辑
    """
    import random
    from datetime import datetime, timedelta
    
    data = []
    
    # 解析日期
    if time_range == 'year':
        start_year = int(start_date)
        end_year = int(end_date)
        dates = [str(year) for year in range(start_year, end_year + 1)]
    else:  # month
        start_year, start_month = map(int, start_date.split('-'))
        end_year, end_month = map(int, end_date.split('-'))
        
        dates = []
        current_year, current_month = start_year, start_month
        while (current_year, current_month) <= (end_year, end_month):
            dates.append(f'{current_year}-{current_month:02d}')
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    
    # 城市列表
    if 'CN' in category:
        cities = ['北京', '上海', '广州', '深圳', '杭州']
    else:
        cities = ['London', 'Manchester', 'Birmingham']
    
    # 生成数据
    for date in dates:
        for city in cities:
            if '气象' in pollutant:
                row = [date, city, random.randint(15, 35), random.randint(40, 80), random.randint(1, 10)]
            elif '建城' in pollutant:
                row = [date, city, round(random.uniform(0.2, 0.8), 3), random.randint(50, 200)]
            else:  # 大气污染数据
                row = [
                    date, city,
                    random.randint(20, 150),  # PM2.5
                    random.randint(30, 200),  # PM10
                    random.randint(10, 80),   # NO2
                    random.randint(50, 200),  # O3
                    random.randint(50, 300)   # AQI
                ]
            data.append(row)
    
    return data

def get_column_info(category, pollutant):
    """获取数据列信息"""
    if '气象' in pollutant:
        return ['日期', '城市', '温度(°C)', '湿度(%)', '紫外辐射强度']
    elif '建城' in pollutant:
        return ['日期', '城市', 'NDVI', '夜光数据']
    else:  # 大气污染数据
        if 'CN' in category:
            return ['日期', '城市', 'PM2.5', 'PM10', 'NO2', 'O3', 'AQI']
        else:
            return ['Date', 'City', 'PM2.5', 'PM10', 'NO2', 'O3', 'AQI']

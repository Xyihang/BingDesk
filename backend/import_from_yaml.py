"""
从 YAML 文件导入课程表
"""
import requests
import yaml

BASE_URL = "http://localhost:8000"

COLORS = {
    "语文": "#1890ff",
    "数学": "#52c41a",
    "英语": "#faad14",
    "物理": "#eb2f96",
    "化学": "#722ed1",
    "政治": "#13c2c2",
    "历史": "#fa541c",
    "体育": "#fadb14",
    "生物": "#52c41a",
    "地理": "#13c2c2",
    "信息技术": "#722ed1",
    "通用技术": "#fa541c",
    "音乐": "#eb2f96",
    "美术": "#fadb14",
    "心理": "#bae7ff",
    "自习": "#8c8c8c",
    "班会": "#8c8c8c",
    "周测": "#ff4d4f",
}

# 读取 YAML 文件
with open('../1.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

subjects = {s['name']: s for s in data['subjects']}
schedules = data['schedules']

print("=" * 60)
print("📚 从 YAML 导入课程表")
print("=" * 60)

# 检查后端
try:
    r = requests.get(f"{BASE_URL}/health", timeout=3)
    print(f"\n✅ 后端服务正常")
except Exception as e:
    print(f"\n❌ 后端服务异常：{e}")
    exit(1)

# 清空旧课程
print("\n🗑️  清空旧课程...")
r = requests.get(f"{BASE_URL}/api/courses")
if r.status_code == 200:
    courses = r.json().get('items', [])
    for course in courses:
        requests.delete(f"{BASE_URL}/api/courses/{course['id']}")
    print(f"✅ 已删除 {len(courses)} 门旧课程")

# 添加新课程
print("\n📅 添加新课程...")
total = 0

for schedule in schedules:
    day = schedule['enable_day']  # 1=周一，2=周二...
    week_type_map = {
        'all': 'all',
        'odd': 'odd',
        'even': 'even'
    }
    week_type = week_type_map.get(schedule.get('weeks', 'all'), 'all')
    
    week_label = {'all': '全周', 'odd': '单周', 'even': '双周'}[week_type]
    day_label = ['','周一','周二','周三','周四','周五','周六','周日'][day]
    
    print(f"\n  {day_label} ({week_label}):")
    
    for cls in schedule['classes']:
        subject_name = cls['subject']
        if subject_name not in subjects:
            continue
            
        subject = subjects[subject_name]
        start_time = cls['start_time']
        end_time = cls['end_time']
        teacher = subject.get('teacher', '')
        classroom = subject.get('room', '')
        color = COLORS.get(subject_name, '#1890ff')
        
        data = {
            "course_name": subject_name,
            "day_of_week": day,
            "start_time": start_time,
            "end_time": end_time,
            "week_type": week_type,
            "teacher": teacher if teacher else None,
            "classroom": classroom if classroom else None,
            "color": color
        }
        
        r = requests.post(f"{BASE_URL}/api/courses", json=data, timeout=5)
        if r.status_code == 200:
            start_str = str(start_time)[:5]
            end_str = str(end_time)[:5]
            print(f"    ✅ {subject_name} {start_str}-{end_str} ({teacher or '无老师'})")
            total += 1
        else:
            print(f"    ❌ {subject_name} 失败：{r.status_code}")

print("\n" + "=" * 60)
print(f"🎉 导入完成！共添加 {total} 节课")
print("📍 访问 http://localhost:5173 查看")
print("=" * 60)

import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ideeza_analytics.settings')
django.setup()

from django.contrib.auth.models import User
from analytics.models import Blog, BlogView

usernames = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry']
blog_templates = [
    {'title': 'Future of AI 2024', 'content': 'AI content...', 'topics': ['AI']},
    {'title': 'Web Dev Practices', 'content': 'Web dev content...', 'topics': ['Web']},
    {'title': 'Django ORM Tips', 'content': 'Django content...', 'topics': ['Django']},
    {'title': 'Microservices', 'content': 'Microservices content...', 'topics': ['Architecture']},
    {'title': 'Data Analytics Pandas', 'content': 'Pandas content...', 'topics': ['Data']},
    {'title': 'REST APIs DRF', 'content': 'API content...', 'topics': ['API']},
    {'title': 'Edge Computing', 'content': 'Edge computing content...', 'topics': ['IoT']},
    {'title': 'ML Deployment', 'content': 'ML content...', 'topics': ['ML']},
    {'title': 'React Vue Angular', 'content': 'Frontend content...', 'topics': ['JavaScript']},
    {'title': 'Database Optimization', 'content': 'DB content...', 'topics': ['Database']}
]
countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Japan', 'Australia', 'India', 'Brazil', 'China', None]
country_tz = {
    'USA': 'America/New_York',
    'Canada': 'America/Toronto',
    'UK': 'Europe/London',
    'Germany': 'Europe/Berlin',
    'France': 'Europe/Paris',
    'Japan': 'Asia/Tokyo',
    'Australia': 'Australia/Sydney',
    'India': 'Asia/Kolkata',
    'Brazil': 'America/Sao_Paulo',
    'China': 'Asia/Shanghai'
}

def create_test_users():
    users = []
    for username in usernames:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com', 'first_name': username.capitalize(), 'last_name': 'Test'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        users.append(user)
        print(f"User created: {username}")
    return users

def create_test_blogs(users):
    blogs = []
    for i, template in enumerate(blog_templates):
        author = random.choice(users)
        country = random.choice(countries)
        days_ago = random.randint(0, 365)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_time = timezone.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        blog = Blog.objects.create(
            title=f"{template['title']} #{i+1}",
            content=template['content'],
            author=author,
            country=country,
            created_at=created_time
        )
        blogs.append(blog)
        print(f"Blog created: {blog.title}")
    return blogs

def create_test_views(blogs, users):
    view_countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Japan', 'Australia', 'India', 'Brazil', 'China']
    total_views = 0
    
    for blog in blogs:
        num_views = random.randint(50, 500)
        blog_created = blog.created_at
        
        for _ in range(num_views):
            viewer = random.choice(users + [None])
            country = random.choice(view_countries)
            
            days_after = random.randint(0, 90)
            if random.random() < 0.7:
                days_after = random.randint(0, 14)
            
            hour = random.choices(
                [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                [0.5, 1, 2, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0.5, 0.2, 0.1],
                k=1
            )[0]
            
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            view_time = blog_created + timedelta(
                days=days_after,
                hours=hour,
                minutes=minute,
                seconds=second
            )
            
            if view_time > timezone.now():
                view_time = timezone.now() - timedelta(hours=random.randint(1, 24))
            
            try:
                tz = pytz.timezone(country_tz.get(country, 'UTC'))
                view_time_tz = view_time.astimezone(tz)
            except:
                view_time_tz = view_time
            
            BlogView.objects.create(
                blog=blog,
                viewer=viewer,
                viewer_country=country,
                viewed_at=view_time_tz
            )
        
        print(f"{num_views} views for: {blog.title}")
        total_views += num_views
    
    print(f"Total views: {BlogView.objects.count()}")
    create_date_test_views(blogs, users)

def create_date_test_views(blogs, users):
    test_dates = [
        ('2024-01-01', 'USA'),
        ('2024-01-02', 'UK'),
        ('2024-01-03', 'Canada'),
        ('2024-01-04', 'Germany'),
        ('2024-01-05', 'France'),
        ('2024-01-06', 'Japan'),
        ('2024-01-07', 'Australia'),
    ]
    
    for date_str, country in test_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = timezone.make_aware(date_obj)
        
        for blog in random.sample(blogs, 3):
            for _ in range(random.randint(5, 20)):
                BlogView.objects.create(
                    blog=blog,
                    viewer=random.choice(users + [None]),
                    viewer_country=country,
                    viewed_at=date_obj + timedelta(hours=random.randint(9, 17))
                )
    
    print("Test date views created")

def check_tz_data():
    print("Checking timezones...")
    blogs = Blog.objects.all()
    for blog in blogs:
        if not timezone.is_aware(blog.created_at):
            print(f"Blog {blog.id} has naive time: {blog.created_at}")
    
    blogviews = BlogView.objects.all()[:100]
    for view in blogviews:
        if not timezone.is_aware(view.viewed_at):
            print(f"View {view.id} has naive time: {view.viewed_at}")
    
    print("Timezone check done")

def main():
    print("Creating test data...")
    print("=" * 50)
    
    BlogView.objects.all().delete()
    Blog.objects.all().delete()
    
    users = create_test_users()
    blogs = create_test_blogs(users)
    create_test_views(blogs, users)
    check_tz_data()
    
    print("=" * 50)
    print("Data creation complete")
    print(f"Users: {User.objects.count()}")
    print(f"Blogs: {Blog.objects.count()}")
    print(f"Views: {BlogView.objects.count()}")
    
    sample_views = BlogView.objects.order_by('viewed_at')[:3]
    for view in sample_views:
        print(f"Sample: {view.viewed_at} - {view.blog.title[:20]} - {view.viewer_country}")

if __name__ == "__main__":
    main()
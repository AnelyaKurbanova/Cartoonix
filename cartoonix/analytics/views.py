import matplotlib
matplotlib.use('Agg')  # Используйте бэкэнд без GUI

import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.db.models import Count, Avg
from social_network.models import Post, Like, Comment

def generate_bar_chart(chart_data):
    categories = [item['category'] for item in chart_data]
    likes = [item['likes'] for item in chart_data]
    comments = [item['comments'] for item in chart_data]

    fig, ax = plt.subplots()

    ax.bar(categories, likes, label='Likes', color='skyblue')
    ax.bar(categories, comments, label='Comments', color='lightgreen', bottom=likes)

    ax.set_xlabel('Categories')
    ax.set_ylabel('Count')
    ax.set_title('Likes and Comments by Category')
    ax.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return image_base64


def generate_pie_chart(pie_data):
    categories = [item['category'] for item in pie_data]
    interactions = [item['interactions'] for item in pie_data]

    fig, ax = plt.subplots()
    ax.pie(interactions, labels=categories, autopct='%1.1f%%', startangle=90,
           colors=['skyblue', 'lightgreen', 'lightcoral', 'orange', 'gold'])
    ax.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return image_base64


def dashboard(request):
    user = request.user  # Получаем текущего пользователя

    # Получаем все посты, созданные текущим пользователем
    posts = Post.objects.filter(author=user).annotate(
        num_likes=Count('likes'),
        num_comments=Count('comments')
    )

    # Общие метрики
    total_posts = posts.count()
    avg_likes = posts.aggregate(avg_likes=Avg('num_likes'))['avg_likes'] or 0
    avg_comments = posts.aggregate(avg_comments=Avg('num_comments'))['avg_comments'] or 0

    # Аналитика по категориям (Пример данных)
    chart_data = [
        {'category': 'Comedy', 'likes': 50, 'comments': 30},
        {'category': 'Drama', 'likes': 40, 'comments': 10},
        {'category': 'Horror', 'likes': 70, 'comments': 20},
    ]

    # Аналитика по круговой диаграмме
    pie_data = [
        {'category': 'Comedy', 'interactions': 80},
        {'category': 'Drama', 'interactions': 50},
        {'category': 'Horror', 'interactions': 90},
    ]

    # Генерация графиков
    bar_chart = generate_bar_chart(chart_data)
    pie_chart = generate_pie_chart(pie_data)

    context = {
        'total_posts': total_posts,
        'avg_likes': avg_likes,
        'avg_comments': avg_comments,
        'bar_chart': bar_chart,
        'pie_chart': pie_chart,
        'top_posts': posts.order_by('-num_likes')[:5],  # Топовые посты по лайкам
    }
    return render(request, 'dashboard.html', context)
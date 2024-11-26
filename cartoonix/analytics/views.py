import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.db.models import Count, Avg
from social_network.models import Post

logger = logging.getLogger('dashboard_logger')


def generate_bar_chart(chart_data):
    try:
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
        logger.info("Bar chart generated successfully.")
        return image_base64
    except Exception as e:
        logger.error(f"Error generating bar chart: {e}")
        return None


def generate_pie_chart(pie_data):
    try:
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
        logger.info("Pie chart generated successfully.")
        return image_base64
    except Exception as e:
        logger.error(f"Error generating pie chart: {e}")
        return None


def dashboard(request):
    user = request.user
    logger.info(f"Dashboard accessed by user {user.username}.")

    try:
        posts = Post.objects.filter(author=user).annotate(
            num_likes=Count('likes'),
            num_comments=Count('comments')
        )

        total_posts = posts.count()
        avg_likes = posts.aggregate(avg_likes=Avg('num_likes'))['avg_likes'] or 0
        avg_comments = posts.aggregate(avg_comments=Avg('num_comments'))['avg_comments'] or 0

        logger.info(f"Total posts: {total_posts}, Avg likes: {avg_likes}, Avg comments: {avg_comments}")

        chart_data = [
            {'category': 'Comedy', 'likes': 50, 'comments': 30},
            {'category': 'Drama', 'likes': 40, 'comments': 10},
            {'category': 'Horror', 'likes': 70, 'comments': 20},
        ]

        pie_data = [
            {'category': 'Comedy', 'interactions': 80},
            {'category': 'Drama', 'interactions': 50},
            {'category': 'Horror', 'interactions': 90},
        ]

        bar_chart = generate_bar_chart(chart_data)
        pie_chart = generate_pie_chart(pie_data)

        if not bar_chart or not pie_chart:
            logger.warning("One or both charts could not be generated.")

        context = {
            'total_posts': total_posts,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'bar_chart': bar_chart,
            'pie_chart': pie_chart,
            'top_posts': posts.order_by('-num_likes')[:5],
        }

        logger.info(f"Dashboard data prepared for user {user.username}.")
        return render(request, 'dashboard.html', context)

    except Exception as e:
        logger.error(f"Error processing dashboard for user {user.username}: {e}")
        return render(request, 'error.html', {'message': 'An error occurred while loading the dashboard.'})

from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'list', views.list),
	url(r'(?P<review_id>\d+)/destroy', views.destroy),
	url(r'(?P<review_id>\d+)/edit', views.edit),
	url(r'(?P<book_id>\d+)', views.view_book),
	url(r'add', views.add),
	url(r'process_book', views.process_book),
	url(r'process_edit', views.process_edit),
	url(r'review_existing', views.review_existing),
	url(r'^$', views.list),
]

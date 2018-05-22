from django.db import models
from apps.users.models import *

class BookManager(models.Manager):
    def basic_validator(self, ReqSession, ReqPost):
        errors = {}
        if ReqPost['book_title']:
            ReqSession['book_title'] = ReqPost['book_title']
        else:
            errors['title_blank'] = "Title must not be blank!"
        if ReqPost.get('existing_author') and ReqPost['existing_author'] != "":
            ReqSession['author_id'] = ReqPost['existing_author']
        else:
            if ReqPost['new_author']:
                ReqSession['author_name'] = ReqPost['new_author']
            else:
                errors['author'] = "You must select an existing author or enter the name of a new author!"
        if ReqPost['review_text']:
            ReqSession['review_text'] = ReqPost['review_text']
            if len(ReqSession['review_text']) < 15:
                errors['review_length'] = "Your review must be at least 15 characters!"
        else:
            errors['review_blank'] = "Your review must not be blank!"
        if ReqPost['rating']:
            ReqSession['rating'] = int(ReqPost['rating'])
            try:
                if ReqSession['rating'] > 5:
                    ReqSession['rating'] = 5
                elif ReqSession['rating'] < 1:
                    ReqSession['rating'] = 1
            except:
                errors['rating_invalid'] = "You must leave a valid rating between 1 and 5 stars!"
        else:
            errors['rating_blank'] = "You must leave a rating!"
        return errors
    def validate_review_for_existing(self, ReqSession, ReqPost):
        errors = {}
        if 'last_viewed_book' in ReqSession:
            ReqSession['book'] = ReqSession['last_viewed_book']
        else:
            errors['no_book'] = "Data for last viewed book not found!"
        if ReqPost['review_text']:
            ReqSession['review_text'] = ReqPost['review_text']
            if len(ReqSession['review_text']) < 15:
                errors['review_length'] = "Your review must be at least 15 characters!"
        else:
            errors['review_blank'] = "Your review must not be blank!"
        if ReqPost['rating']:
            ReqSession['rating'] = int(ReqPost['rating'])
            try:
                if ReqSession['rating'] > 5:
                    ReqSession['rating'] = 5
                elif ReqSession['rating'] < 1:
                    ReqSession['rating'] = 1
            except:
                errors['rating_invalid'] = "You must leave a valid rating between 1 and 5 stars!"
        else:
            errors['rating_blank'] = "You must leave a rating!"
        return errors
    def submit_review(self, ReqSession):
        if 'author_id' in ReqSession:
            if len(Book.objects.filter(title=ReqSession['book_title'], author =Author.objects.get(id = ReqSession['author_id']))) > 0:
                author = Author.objects.get(id=ReqSession['author_id'])
                book = Book.objects.get(title=ReqSession['book_title'], author = author)
            else:
                author = Author.objects.get(id=ReqSession['author_id'])
                book = Book(title=ReqSession['book_title'], author = author)
                book.save()
        elif 'author_name' in ReqSession:
            author = Author(name=ReqSession["author_name"])
            author.save()
            book = Book(title=ReqSession['book_title'], author=author)
            book.save()
        else:
            errors['invalid_author'] = "Your review must contain a valid author!"
            return False
        if 'id' in ReqSession:
            user = User.objects.get(id=ReqSession['id'])
        else:
            user = User.objects.get(id=0)
        review = Review(content = ReqSession['review_text'], book = book, reviewer=user, rating=ReqSession['rating'])
        review.save()

        del ReqSession['book_title']
        del ReqSession['review_text']
        if 'author_id' in ReqSession:
            del ReqSession['author_id']
        elif 'author_id' in ReqSession:
            del ReqSession['author_name']
        del ReqSession['rating']

        return review
    def submit_review_for_existing(self, ReqSession):
        if 'id' in ReqSession:
            user = User.objects.get(id=ReqSession['id'])
        else:
            user = User.objects.get(id=0) #saves as guest account
        if 'book' in ReqSession:
            book = Book.objects.get(id=ReqSession['book'])
        else:
            errors['no_book_found'] = "No book found. Try again with cookies enabled."
            return False

        review = Review(content = ReqSession['review_text'], book = book, reviewer = user, rating = ReqSession['rating'])
        review.save()

        del ReqSession['book']
        del ReqSession['review_text']
        del ReqSession['rating']

        return review
        
class ReviewManager(models.Manager):
    def delete_selected(self, ReqSession, review_id):
        review = Review.objects.get(id=int(review_id))
        book_id = review.book_id
        if 'id' in ReqSession:
            if ReqSession['id'] == review.reviewer.id and ReqSession['id'] != 0:
                review.delete()
                return True
        return False
    def edit_validation(self, ReqSession, ReqPost):
        errors = {}
        try:
            review = Review.objects.get(id=int(ReqSession['review_id']))
            book_id = review.book_id
            if 'id' in ReqSession:
                if ReqSession['id'] == review.reviewer.id and ReqSession['id'] != 0:
                    if ReqPost['review_text']:
                        ReqSession['review_text'] = ReqPost['review_text']
                        if len(ReqSession['review_text']) < 15:
                            errors['review_length'] = "Your review must be at least 15 characters!"
                    else:
                        errors['review_blank'] = "Your review must not be blank!"
                    if ReqPost['rating']:
                        ReqSession['rating'] = int(ReqPost['rating'])
                        try:
                            if ReqSession['rating'] > 5:
                                ReqSession['rating'] = 5
                            elif ReqSession['rating'] < 1:
                                ReqSession['rating'] = 1
                        except:
                            errors['rating_invalid'] = "You must leave a valid rating between 1 and 5 stars!"
                            return errors
            return errors
        except:
            errors['edit_failed'] = "Unable to process your edit request. Please try again."
            return errors
    def edit_process(self, ReqSession):
        if 'id' in ReqSession:
            user = User.objects.get(id=ReqSession['id'])
        else:
            return False 
        if 'review_id' in ReqSession:
            review = Review.objects.get(id=int(ReqSession['review_id']))
        else:
            return False
        if not ReqSession['id'] == review.reviewer.id:
            return False

        review.content = ReqSession['review_text']
        review.rating = ReqSession['rating']
        review.save()

        del ReqSession['review_id']
        del ReqSession['review_text']
        del ReqSession['rating']

        return review

class Author(models.Model):
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Book(models.Model):
    title = models.CharField(max_length = 255)
    author = models.ForeignKey(Author)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = BookManager()

class Review(models.Model):
    content = models.TextField(default="")
    book = models.ForeignKey(Book)
    reviewer = models.ForeignKey('users.User')
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = ReviewManager()

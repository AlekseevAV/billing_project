from rest_framework.routers import DefaultRouter

from .views import AccountsView, TransactionsView


router = DefaultRouter()
router.register(r'accounts', AccountsView, basename='accounts')
router.register(r'transactions', TransactionsView, basename='transactions')


urlpatterns = router.urls

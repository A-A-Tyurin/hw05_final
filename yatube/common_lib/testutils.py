from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.urls import reverse

from yatube.settings import PAGINATOR_PAGE_SIZE


class AppTestBase:
    def __init__(self):
        self.current_client = None

    def switch_client(self, login_required):
        self.current_client = (self.guest_client
                               if not login_required else
                               self.authorized_client)


class AppUrlsTestBase(AppTestBase):

    URL_GENERATION_MSG = 'URL генерируется не правильно.'
    PAGE_NOT_FOUND_MSG = 'Страница не доступна.'
    INCORRECT_TEMPLATE = 'Страница использует не корректный шаблон.'

    LOGIN_URL = reverse('login')

    def test_page_links(self):
        for url, link, _, _ in [url_dict.values() for url_dict in self.urls]:
            with self.subTest(url=url, link=link):
                self.assertEqual(url, link, self.URL_GENERATION_MSG)

    def test_page_exists_at_desired_location(self):
        values = [url_dict.values() for url_dict in self.urls]
        for _, link, login_required, _ in values:
            with self.subTest(link=link):
                self.switch_client(login_required)

                response = self.current_client.get(link)
                self.assertEqual(
                    response.status_code, 200, self.PAGE_NOT_FOUND_MSG
                )

    def test_page_redirect_anonymous(self):
        urls = [url for url in self.urls if url['login_required']]
        for _, link, _, _ in [url_dict.values() for url_dict in urls]:
            with self.subTest(link=link):
                response = self.guest_client.get(link, follow=True)
                self.assertRedirects(
                    response,
                    f'{self.LOGIN_URL}?next={link}'
                )

    def test_page_template(self):
        values = [url_dict.values() for url_dict in self.urls]
        for _, link, login_required, template in values:
            with self.subTest(link=link):
                self.switch_client(login_required)

                response = self.current_client.get(link)
                self.assertTemplateUsed(
                    response, template, self.INCORRECT_TEMPLATE
                )


class AppViewsTestBase(AppTestBase):

    CONTEXT_OBJ_NONE_MSG = 'Объект не передан в контекст.'
    CONTEXT_OBJ_TYPE_MSG = 'Тип объекта не соответствует ожидаемому.'
    EXCEPTED_OBJ_MSG = 'Ожидаемый объект отсутствует.'

    def test_object_types_in_context(self):

        for config_item in self.test_config:
            login_required = config_item['login_required']
            self.switch_client(login_required)

            url = config_item['url']
            resp = self.current_client.get(url)
            context_names_obj_types = config_item['context_names_obj_types']

            for context_name, object_type in context_names_obj_types:
                with self.subTest(url=url, context_name=context_name,
                                  object_type=object_type):

                    cntxt_obj = resp.context.get(context_name)
                    self.assertIsNotNone(cntxt_obj, self.CONTEXT_OBJ_NONE_MSG)

                    if isinstance(cntxt_obj, QuerySet):
                        self.assertTrue(cntxt_obj.count() > 0)
                        self.assertTrue(all(
                            isinstance(obj, object_type) for obj in cntxt_obj),
                            self.CONTEXT_OBJ_TYPE_MSG
                        )
                    else:
                        self.assertIsInstance(
                            cntxt_obj, object_type, self.CONTEXT_OBJ_TYPE_MSG
                        )

                        if object_type is Page:
                            self.assertIsInstance(
                                cntxt_obj.paginator,
                                Paginator,
                                self.CONTEXT_OBJ_TYPE_MSG
                            )
                            self.assertEqual(
                                cntxt_obj.paginator.per_page,
                                PAGINATOR_PAGE_SIZE
                            )

    def test_object_in_query_set(self):

        for config_item in self.test_config:
            login_required = config_item['login_required']
            self.switch_client(login_required)

            url = config_item['url']
            resp = self.current_client.get(url)
            context_names_obj_types = config_item['context_names_obj_types']

            for context_name, object_type in context_names_obj_types:
                with self.subTest(url=url, context_name=context_name,
                                  object_type=object_type):

                    context_obj = resp.context_data.get(context_name)
                    excepted_objs = config_item['excepted_objs']

                    if excepted_objs:
                        for obj in excepted_objs:
                            if isinstance(obj, object_type):
                                if isinstance(context_obj, QuerySet):
                                    self.assertIn(
                                        obj, context_obj, self.EXCEPTED_OBJ_MSG
                                    )
                                else:
                                    self.assertEqual(
                                        obj, context_obj, self.EXCEPTED_OBJ_MSG
                                    )


class AppModelsTestBase():
    OBJ_TO_STR_MSG = 'Проверьте правильность работы метода __str__().'
    OBJ_VERBOSE_NAMES_MSG = 'verbose_name указан не верно.'
    OBJ_HELP_TEXT_MSG = 'help_text указан не верно.'

    def test_object_to_str(self):
        for config_item in self.test_config:
            obj = config_item['obj']
            excepted_str = config_item['excepted_str']

            with self.subTest(obj=obj):
                self.assertEquals(str(obj), excepted_str, self.OBJ_TO_STR_MSG)

    def test_object_verbose_name(self):
        for config_item in self.test_config:
            obj = config_item['obj']
            verbose_names = config_item['verbose_names']

            for value, expected in verbose_names.items():
                with self.subTest(obj=obj, value=value):
                    self.assertEqual(
                        obj._meta.get_field(value).verbose_name,
                        expected,
                        self.OBJ_VERBOSE_NAMES_MSG
                    )

    def test_object_help_text(self):
        for config_item in self.test_config:
            obj = config_item['obj']
            help_text = config_item['help_text']

            for value, expected in help_text.items():
                with self.subTest(obj=obj, value=value):
                    self.assertEqual(
                        obj._meta.get_field(value).help_text,
                        expected,
                        self.OBJ_HELP_TEXT_MSG
                    )

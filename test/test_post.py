from . import AniconDivaTestCase
from tools import fake_data_gen

class TestPost(AniconDivaTestCase):
    def test_post_creation(self):

        for i in range(1, 500):
            random_data = fake_data_gen.generate_row(i)
            # Example test for creating a post
            response = self.client.post('/create_post', data={
                'nickname': random_data[1],
                'content': random_data[2]
            })

            self.assert_status(response, 302)
            self.assert_message_flashed(f"投稿成功，您的匿名ID是：" + str(random_data[0]), 'new_id')

    def test_view_post(self):
        """測試查看單篇文章 (ID)"""
        post_id = 1  # 假設要查看的文章ID
        response = self.client.get(f'/view_post?query={post_id}')
        self.assert_status(response, 200)

    def test_view_non_existent_post(self):
        """測試查看不存在的文章 (ID)"""
        post_id = 9999
        response = self.client.get(f'/view_post?query={post_id}')
        self.assert_status(response, 200)
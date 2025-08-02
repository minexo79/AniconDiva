from . import AniconDivaTestCase
from tools import fake_data_gen

class TestPost(AniconDivaTestCase):
    def test_post_creation(self):

        for i in range(1, 501):
            random_data = fake_data_gen.generate_row(i)
            # Example test for creating a post
            response = self.client.post('/create_post', data={
                'nickname': random_data[1],
                'content': random_data[2]
            })

            self.assert_status(response, 302)
            self.assert_message_flashed(f"投稿成功，您的匿名ID是：" + str(random_data[0]), 'new_id')
import random
from color.models import Color
from django.db.models import Max
from itertools import chain


def judge_sign(num):
    if num >= 0:
        return 1
    else:
        return -1


class RGBColor:
    def __init__(self, *, r=-1, g=-1, b=-1, code=''):
        if code and r == -1 and g == -1 and b == -1:  # codeのみ
            rgb_dict = self.code_to_rgb(code)
            self.code = code
            self.r = rgb_dict['r']
            self.g = rgb_dict['g']
            self.b = rgb_dict['b']
        elif code == '' and 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:  # RGBのみ
            code = self.rgb_to_code(r, g, b)
            self.code = code
            self.r = r
            self.g = g
            self.b = b
        else:
            raise TypeError('引数が正しくありません')

    @staticmethod
    def code_to_rgb(code):
        r = int(code[1:3], 16)
        g = int(code[3:5], 16)
        b = int(code[5:7], 16)
        rgb_dict = {'r': r, 'g': g, 'b': b}
        return rgb_dict

    @staticmethod
    def rgb_to_code(r, g, b):
        code = '#'
        for num in (r, g, b):
            hex_num = format(num, 'x')  # 16進数に変換
            code += hex_num.zfill(2)    # ゼロパディング
        return code

    def sum_rgb(self):
        return sum((self.r, self.g, self.b))

    def categorize(self):
        if self.r == self.g == self.b:
            category = 'mono'
        else:
            max_rgb = max(self.r, self.g, self.b)  # 最大値で割って比率を求める
            r_rate = self.r / max_rgb
            g_rate = self.g / max_rgb
            b_rate = self.b / max_rgb
            criteria = 0.75  # 適当
            while r_rate >= criteria and g_rate >= criteria and b_rate >= criteria:
                criteria += (1 - criteria) / 2  # rgb全てが基準を満たす場合、基準を厳しくする
            if r_rate >= criteria:
                if g_rate >= criteria:
                    category = 'yellow'
                elif b_rate >= criteria:
                    category = 'magenta'
                else:
                    category = 'red'
            elif g_rate >= criteria:
                if b_rate >= criteria:
                    category = 'cyan'
                else:
                    category = 'green'
            else:
                category = 'blue'
        return category

    def __sub__(self, other):
        a = 1  # 補正

        diff_r = self.r - other.r
        diff_g = self.g - other.g
        diff_b = self.b - other.b

        sum_sign = judge_sign(diff_r) + judge_sign(diff_g) + judge_sign(diff_b)

        if abs(sum_sign) == 3:  # rgbがそれぞれ同方向にずれている場合
            a = 0.7  # 明度が異なるだけの色の、差の値を小さくする

        sq_diff_r = diff_r ** 2
        sq_diff_g = diff_g ** 2
        sq_diff_b = diff_b ** 2
        diff = (((sq_diff_r + sq_diff_g + sq_diff_b) / 3) ** 0.5) * a
        return diff

    def __str__(self):
        return 'R' + str(self.r) + ' G' + str(self.g) + ' B' + str(self.b)


class OrderColor:
    @staticmethod
    def order_by_sum_rgb(colors, reverse=False):
        order_list = []
        order_dict = {}

        for color in colors:
            sum_rgb = RGBColor(code=color.code).sum_rgb()
            if sum_rgb in order_dict:  # 同じ値が存在した場合
                sum_rgb += random.random()  # 0-1の乱数を加える
            order_list.append(sum_rgb)
            order_dict[sum_rgb] = color

        order_list.sort(reverse=reverse)

        color_list = []
        for sum_rgb in order_list:
            color_list.append(order_dict[sum_rgb])

        return color_list

    @staticmethod
    def order_by_similar(colors, target_color):
        """
        対象色と距離が近い順に並び替え
        """
        target_rgb = RGBColor(code=target_color.code)
        order_list = []
        order_dict = {}
        for color in colors:
            rgb = RGBColor(code=color.code)
            diff = target_rgb - rgb
            if diff in order_dict:
                diff += random.random()
            order_list.append(diff)
            order_dict[diff] = color

        order_list.sort()  # 差が小さい順にソート

        color_list = []
        for diff in order_list:
            color_list.append(order_dict[diff])

        return color_list

    @staticmethod
    def order_by_category(colors, reverse=False):
        colors_list = [[], [], [], [], [], [], []]
        for color in colors:
            cate = RGBColor(code=color.code).categorize()
            if cate == 'red':
                colors_list[0].append(color)
            elif cate == 'yellow':
                colors_list[1].append(color)
            elif cate == 'green':
                colors_list[2].append(color)
            elif cate == 'cyan':
                colors_list[3].append(color)
            elif cate == 'blue':
                colors_list[4].append(color)
            elif cate == 'magenta':
                colors_list[5].append(color)
            else:
                colors_list[6].append(color)

        for index, colors in enumerate(colors_list[:]):
            colors_list[index] = OrderColor.order_by_sum_rgb(colors, reverse=reverse)  # 色の種類ごとにソート

        color_list = list(chain.from_iterable(colors_list))  # フラットなリストに変換

        return color_list


def get_random_colors(num):
    max_id = Color.objects.all().aggregate(max_id=Max('id'))['max_id']
    id_list = list(range(1, max_id+1))
    random.shuffle(id_list)

    color_list = []
    count = 0
    for id in id_list:  # 削除したデータのIDが抜けているため、全IDのリストを使ってcountで個数を調整
        if count >= num:
            break
        try:
            color_list.append(Color.objects.get(id=id))
        except Color.DoesNotExist:
            continue
        count += 1
    return color_list


def create_choices(color, difficulty=2):
    similar_colors = OrderColor.order_by_similar(Color.objects.all(), color)
    correct_color = similar_colors[0]
    if difficulty == 3:
        choices = random.sample(similar_colors[2:7], 3)
    elif difficulty == 2:
        choices = random.sample(similar_colors[4:9], 3)
    else:
        choices = random.sample(similar_colors[6:11], 3)

    choices.append(correct_color)
    random.shuffle(choices)
    return choices


if __name__ == '__main__':
    TEST_CODE = '#ffffff'
    TEST_DIC = {'r': 230, 'g': 255, 'b': 0}
    rgb_color1 = RGBColor(**TEST_DIC)
    rgb_color2 = RGBColor(code=TEST_CODE)
    print(rgb_color1.categorize(), rgb_color2.categorize())

a = 'aa'
b = 'bb'
tuple_ = (a, b)
dict_ = {'c': 'cc', 'd': 'dd'}


def test(*args, **kwargs):
    print(args)
    for item in args:
        print(item)
    print(kwargs)
    for key, value in kwargs.items():
        print(key, value)


if __name__ == '__main__':
    test('vv', 'ww', x='xx', y='yy', *tuple_, **dict_)

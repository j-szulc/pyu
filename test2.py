from pyu.cli_to_lib import PatchedArgumentParser

def f():
    return 1/0

def g():
    return f()

def h():
    return g()

if __name__ == '__main__':
    parser = PatchedArgumentParser()
    parser.add_argument('--foo', required=True, type=str)
    parser.add_argument('--bar', default=None, type=str)
    args = parser.parse_args()
    if args.bar:
        h()
    print(open(args.foo).read().upper())
import pyu.cli_to_lib
import sys
print(sys.argv)
print("Hello")


x = [1]

if __name__ == '__main__':
    parser = pyu.cli_to_lib.PatchedArgumentParser()
    parser.add_argument('--foo', required=True, type=int)
    args = parser.parse_args()
    print(args.foo**2)

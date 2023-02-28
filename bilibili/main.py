from bili_client import BiliClient
import argparse


def callback(res_body):
    # TODO call back implementation
    raise NotImplementedError


def main():
    bili = BiliClient(**vars(args))
    bili.register_hook(callback)
    bili.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('roomID', type=str, help='room ID')
    parser.add_argument('key', type=str, help='key')
    parser.add_argument('secret', type=str, help='str')
    parser.add_argument('--host', default='live-open.biliapi.com', help='host')
    args = parser.parse_args()

    main()

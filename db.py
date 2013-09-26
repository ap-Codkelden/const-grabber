import json
import sys
from db_handle import db_handle
import argparse

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("-u", '--user-id', type=int, default=0, \
                        action='store', help="User ID")

arg_parser.add_argument('-p', '--print', help='print BL', \
                        action='store_true', default=False, dest='print')

arg_parser.add_argument('-r', '--remove', help='remove user from BL', \
                        action='store_true', default=False, dest='remove')

arg_parser.add_argument('-a', '--add', help='add user to BL', \
                        action='store_true', default=False, dest='add')


def main():
   args = arg_parser.parse_args()
   db = db_handle()
   if len(sys.argv) == 1:
      arg_parser.print_help()
   else:
      if len(sys.argv) == 2:
         if args.print:
            db.showBlackList()
         else:
            print("You specify a few args.")
      elif len(sys.argv) == 3:
         print ("Wrong set of arguments")
      elif len(sys.argv) == 4:
         try:
            if args.add and args.user_id>0:
               db.addUserToBL(args.user_id)
            elif args.remove and args.user_id>0:
               db.delUserFromBL(args.user_id)
            else:
               print("Error!")
         except TypeError:
            print ("UID must be positive integer")


if __name__ == '__main__':
   main()
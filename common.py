from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pathlib import Path
import logging
from datetime import datetime
import traceback
import time

from rdemail import send_email

def do_it(broker_do_it, args):
  success = False
  driver = None
  try:
    user_agent = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    options = Options()
    options.add_argument("--headless")  # Remove this if you want to see the browser (Headless makes the chromedriver not have a GUI)
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    success = broker_do_it(driver=driver, args=args)
  except Exception as e:
    print(datetime.now(), e)
    traceback.print_exception(e)
    if driver is not None:
      driver.save_screenshot(args.log_dir/"exception.png")
      logging.info(f'url {driver.current_url}')
  if driver is not None:
    driver.quit()
  send_email(send_to=args.gmail_id, send_from_gmail=args.gmail_id,
      subject=f"TT {args.client_id} {success} {args.email_tag}",
      contents="check logs", interactive=False,
      gmail_app_password=args.gmail_app_password)
  return success
    
def do_common_args_and_do_it(logger_file: str, parser,
    broker_do_it, update_args=None):
  parser.add_argument("--logger_file",
      help="logger output filename", default=logger_file)
  parser.add_argument("--log_dir", type=Path,
      default=Path.cwd())
  # python >= 3.11 required for below
  # parser.add_argument("--log_level", default="INFO",
  #     help="python logging.LEVEL",
  #     choices=set(logging.getLevelNamesMapping().keys()))
  parser.add_argument("--client_id", required=True,
                      help="Broker Client Code e.g. TNR01")
  parser.add_argument("--gmail_id", required=True,
                      help="can be same as TT login id")
  parser.add_argument("--gmail_app_password", required=True,
                      help="Gmail App password")
  parser.add_argument("--tt_login_id", required=False,
                      help="TT login id if not same as gmail_id")
  parser.add_argument("--email_tag", required=False,
                      help="Additional text in email subject")
  parser.add_argument("--sleep_sec", type=int, default=300,
                      help="sleep seconds inbetween retries")
  parser.add_argument("--retries", type=int, default=1,
                      help="number of retries")
  args = parser.parse_args()
  log_format = "[%(asctime)s:%(levelname)8s():%(name)s:%(filename)s" \
    ":%(lineno)s:%(funcName)15s() ] %(message)s"
  logging.basicConfig(level="INFO", format=log_format,
    filename=args.log_dir/args.logger_file)
  logging.info(args)
  print("started at ", datetime.now())
  if not do_it(args=args, broker_do_it=broker_do_it):
    for retry in range(2, args.retries+2):
      time.sleep(args.sleep_sec)
      if update_args is not None:
        args = update_args(args=args, retry=retry)
      logging.info("Retrying...")
      if do_it(args=args, broker_do_it=broker_do_it):
        break

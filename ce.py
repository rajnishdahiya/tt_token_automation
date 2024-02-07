#! /usr/bin/env python3


from selenium.webdriver.common.by import By
from selenium_recaptcha_solver import RecaptchaSolver
from selenium_recaptcha_solver import StandardDelayConfig
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys as keys
from selenium.common.exceptions import TimeoutException

import argparse
import logging
import pathlib
import sys
import time
import traceback
import pyotp
import requests
from datetime import datetime

import common
from rdemail import send_email

def update_args(args, retry: int):
  if args.min_delay is not None:
    args.min_delay = (retry+1)*args.min_delay
  if args.max_delay is not None:
    args.max_delay = (retry+1)*args.max_delay
  return args

def do_it(args, driver):
  # let's get access token from CE 1st
  totp_url = "https://xts.compositedge.com/interactive/auth/verifytotp"
  totp = pyotp.TOTP(args.totp)
  resp = requests.post(totp_url, {"source": "WEBAPI", "userID": args.client_id,
      "deviceType": "WEB", "pin": str(totp.now()),
      "appKey": args.api_key})
  result_key = "result"
  access_token_key = "accessToken"
  if 200 != resp.status_code \
      or "application/json" not in resp.headers.get("Content-Type")\
      or result_key not in resp.json().keys()\
      or access_token_key not in resp.json().get(result_key).keys():
    logging.error(f'{resp.content}, {resp.status_code}')
    sys.exit()
  access_token = resp.json().get(result_key).get(access_token_key)
  delay_config=StandardDelayConfig()
  if None not in (args.min_delay, args.max_delay) and args.max_delay > args.min_delay:
    delay_config = StandardDelayConfig(min_delay=args.min_delay, max_delay=args.max_delay)
  solver = RecaptchaSolver(driver=driver, delay_config=delay_config)
  tt_login_url = "https://tradetron.tech/login"
  driver.get(url=tt_login_url)
  time.sleep(5)
  driver.save_screenshot(args.log_dir/"login.png")
  recaptcha_iframe = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.TAG_NAME, 'iframe')))
  try:
    solver.click_recaptcha_v2(iframe=recaptcha_iframe)
  except TimeoutException as e:
    print(datetime.now())
    traceback.print_exception(e)
    logging.info("Maybe it worked!")
  time.sleep(2)
  driver.save_screenshot(args.log_dir/"captca.png")
  email_element = driver.find_element(By.ID, "email")
  if args.tt_login_id is not None:
    email_element.send_keys(args.tt_login_id)
  else:
    email_element.send_keys(args.gmail_id)
  password_element = driver.find_element(By.ID, "password")
  password_element.send_keys(args.password)
  driver.save_screenshot(args.log_dir/"filled.png")
  submit_button = driver.find_element(By.XPATH, '//button[text()="Sign in"]')
  submit_button.submit()
  time.sleep(5)
  driver.save_screenshot(args.log_dir/"loggedin.png")
  def check_title_and_send_email_on_failure(title: str):
    if str(driver.title) != title:
      email_subject = f"TT CE {args.client_id} {title} failed"
      send_email(send_to="cserajnishdahiya@gmail.com",
          subject=email_subject, send_from_gmail=args.gmail_id,
          contents="check logs", interactive=False,
          gmail_app_password=args.gmail_app_password)
      driver.quit()
      driver.save_screenshot(args.log_dir/"failure.png")
      sys.exit("check_title_and_send_email_on_failure failed")
  check_title_and_send_email_on_failure("Dashboard")
  driver.get(url="https://tradetron.tech/user/broker-and-exchanges")
  driver.save_screenshot(args.log_dir/"brokers.png")
  time.sleep(5)
  check_title_and_send_email_on_failure("Brokers & Exchanges")
  def get_ce_button_by_title(title: str):
    ce_td = driver.find_element(By.XPATH, '//td[contains(text(), "Compositedge")]')
    ce_tr = ce_td.find_element(By.XPATH, "..")
    ce_button = ce_tr.find_element(By.XPATH, f'.//a[@title="{title}"]')
    return ce_button
  get_ce_button_by_title("Edit").click()
  time.sleep(5)
  logging.info(f'url {driver.current_url}')
  driver.save_screenshot(args.log_dir/"settings-before.png")
  check_title_and_send_email_on_failure("Brokers & Exchanges")
  secret_elem = driver.find_element(By.ID, "label_1")
  secret_elem.send_keys(keys.CONTROL, 'a')
  secret_elem.send_keys(keys.BACKSPACE)
  secret_elem.send_keys(args.secret_key)
  api_elem = driver.find_element(By.ID, "label_2")
  api_elem.send_keys(keys.CONTROL, 'a')
  api_elem.send_keys(keys.BACKSPACE)
  api_elem.send_keys(args.api_key)
  token_elem = driver.find_element(By.ID, "label_6")
  token_elem.send_keys(keys.CONTROL, 'a')
  token_elem.send_keys(keys.BACKSPACE)
  token_elem.send_keys(access_token)
  driver.save_screenshot(args.log_dir/"settings-after.png")
  save_button = driver.find_element(By.XPATH, '//button[contains(text(), "Save")]')
  save_button.click()
  time.sleep(5)
  driver.save_screenshot(args.log_dir/"saved.png")
  logging.info(f'url {driver.current_url}')
  get_ce_button_by_title("Re-generate Token").click()
  time.sleep(2)
  driver.save_screenshot(args.log_dir/"generated.png")
  driver.find_element(By.XPATH, '//*[contains(text(), "Token generated succesfully")]')
  return True

def parse_args_and_do_it(logger_file: str):
  parser = argparse.ArgumentParser(
      description="Composite (Symphony) TOTP based Token Refresh for TT",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--totp", required=True,
                      help="TOTP key")
  parser.add_argument("--api_key", required=True,
                      help="API key")
  parser.add_argument("--secret_key", required=True,
                      help="secret key")
  parser.add_argument("--password", required=True,
                      help="TT password")
  parser.add_argument("--min_delay", type=float,
                      help="min_delay parameter of StandardDelayConfig")
  parser.add_argument("--max_delay", type=float,
                      help="max_delay parameter of StandardDelayConfig")
  common.do_common_args_and_do_it(logger_file=logger_file,
      parser=parser, broker_do_it=do_it, update_args=update_args)

if __name__ == "__main__":
  stem = pathlib.PurePath(__file__).stem
  parse_args_and_do_it(stem + ".log")

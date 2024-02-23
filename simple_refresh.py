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
import time
import traceback
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
  driver.get(url=args.refresh_icon_url)
  time.sleep(2)
  driver.save_screenshot(args.log_dir/"generated.png")
  driver.find_element(By.XPATH, '//*[contains(text(), "Token generated succesfully")]')
  return True

def parse_args_and_do_it(logger_file: str):
  parser = argparse.ArgumentParser(
      description="Simply Click on Refresh Icon",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--refresh_icon_url", required=True,
      help="e.g. https://tradetron.tech/user/broker-and-exchanges/regenerate-token/414")
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

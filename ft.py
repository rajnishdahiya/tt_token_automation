#! /usr/bin/env python3

from selenium.webdriver.common.by import By
import argparse
import time
import pathlib

import common

def do_it(args, driver):
  driver.get(args.auth_url)
  time.sleep(5)
  # print(driver.page_source.encode('utf-8'))
  username_element = driver.find_element(By.ID,'input-17')
  username_element.send_keys(args.client_id)
  password_element = driver.find_element(By.ID,'pwd')
  password_element.send_keys(args.password)
  otp_element = driver.find_element(By.ID,'pan')
  otp_element.send_keys(args.dob)
  submit_button = driver.find_element(By.ID,'sbmt')
  submit_button.click()
  time.sleep(5)
  success_url_suffix = "tradetron.tech/html-view/success"
  # multiple attemps in a day might lead to additional user confirmation
  if not str(driver.current_url).endswith(success_url_suffix):
    cont_button = driver.find_element(By.XPATH,
        '//button[normalize-space()="Continue"]')
    cont_button.click()
    time.sleep(5)
  return str(driver.current_url).endswith(success_url_suffix)

def parse_args_and_do_it(logger_file: str):
  parser = argparse.ArgumentParser(
      description="Flattrade Token Refresh for TT",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--password", required=True,
                      help="Flattrade password")
  parser.add_argument("--dob", required=True,
                      help="Date of Birth in DDMMYYYY format")
  parser.add_argument("--auth_url", required=True,
                      help="TT Flattrade Auth URL")
  common.do_common_args_and_do_it(logger_file=logger_file, parser=parser,
      broker_do_it=do_it)

if __name__ == "__main__":
  stem = pathlib.PurePath(__file__).stem
  parse_args_and_do_it(stem + ".log")

#! /usr/bin/env python3

import argparse
from pathlib import Path
import yagmail

def send_email(send_to, subject, contents, send_from_gmail,
               gmail_app_password, interactive : bool):
  """
  :param send_to:
  :param subject:
  :param text:

  :return:
  """
  smtp_server = "smtp.gmail.com"
  smtp_port = None
  smtp_ssl = True
  email_tags = ""
  parent = Path(__file__).resolve().parent
  smtp_server_file = parent/"smtp-server.txt"
  if (smtp_server_file.is_file()):
    smtp_server = open(smtp_server_file, mode="r").readline().strip()
    smtp_ssl = False
  smtp_port_file = parent/"smtp-port.txt"
  if (smtp_port_file.is_file()):
    smtp_port = int(open(smtp_port_file, mode="r").readline())
    smtp_ssl = False
  email_tags_file = parent/"email-tags.txt"
  if (email_tags_file.is_file()):
    email_tags = open(email_tags_file, mode="r").readline().strip()
  print("smtp_server", smtp_server, "smtp_port", smtp_port,
        "send_to", send_to, "subject", subject, "contents",
        contents, "smtp_ssl", smtp_ssl, "email_tags", email_tags)
  with yagmail.SMTP(user=send_from_gmail, password=gmail_app_password,
                    port=smtp_port, host=smtp_server, smtp_ssl=smtp_ssl,
                    timeout = 10) as yag:
    yag.set_logging(yagmail.logging.DEBUG,
                    file_path_name=Path.home()/"yagmail.log")
    try:
      send_result = yag.send(to=send_to, subject=email_tags+subject,
                             contents=contents,
                             preview_only=(interactive is not False))
      if send_result is False:
        print("WARN couldn't send email!", send_result)
      print("Email sent successfully")
    except Exception as e:
      print("WARN send email failed", e)
  
if __name__ == "__main__": 
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--gmail_id", required=True,
                      help="send from")
  parser.add_argument("--gmail_app_password", required=True,
                      help="Gmail App password")
  parser.add_argument("-s", "--send_to", nargs='+',
      required=True, help="list of receivers")
  parser.add_argument("--subject",
      required=True, help="email subject")
  parser.add_argument("-c", "--contents", nargs='+',
      help="list of contents (text, html, files)")
  parser.add_argument('--interactive', action=argparse.BooleanOptionalAction)
  args = parser.parse_args()
  send_email(send_to=args.send_to, subject=args.subject,
      contents=args.contents, interactive=args.interactive,
      send_from_gmail=args.gmail_id,
      gmail_app_password=args.gmail_app_password)

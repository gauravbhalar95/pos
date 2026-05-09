from flask import *
import mysql.connector as myconn
import base64
import qrcode
import time
from datetime import datetime
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A5, A4
from reportlab.pdfgen import canvas
import os
from openpyxl import Workbook
import datetime
from werkzeug.security import *
from escpos.printer import Usb, Network, Serial
import usb.core
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

libery_db = Blueprint("libery", __name__)








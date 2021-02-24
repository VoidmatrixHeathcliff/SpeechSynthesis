# -*- coding: UTF-8 -*-

import os
import time
import _thread
import hashlib
import requests
import configparser
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
from urllib.parse import quote
from tkinter import scrolledtext

config = configparser.ConfigParser()

token = ""
cfgData = {}


def processConfigFile():
    if os.path.exists('./config.ini'):
        try:
            global cfgData
            config.read("./config.ini", encoding='utf-8')
            API_KEY = config.get("default", "API_KEY").strip()
            SECRET_KEY = config.get("default", "SECRET_KEY").strip()
            if API_KEY == "" or SECRET_KEY == "":
                tkinter.messagebox.showwarning(title='错误', message='配置信息不可为空，请重新填写配置文件！')
                window.destroy()
                window.quit()
            cfgData = {"API_KEY": API_KEY, "SECRET_KEY": SECRET_KEY}
        except:
            tkinter.messagebox.showerror(title='错误', message='读取配置信息失败，请重新填写配置文件！')
            window.destroy()
            window.quit()
    else:
        tkinter.messagebox.showwarning(title='警告', message='未检测到配置文件，工具将自动生成空白配置文件，请前往填写完善后使用！')
        try:
            with open('./config.ini', 'w', encoding='utf-8') as file:
                data = '[default]\n\nAPI_KEY=\n\nSECRET_KEY='
                file.write(data)
        except:
            tkinter.messagebox.showerror(title='错误', message='生成空白配置文件失败，请手动生成并填写配置文件！')
        window.destroy()
        window.quit()


def getToken(cfgData):
    API_KEY = cfgData["API_KEY"]
    SECRET_KEY = cfgData["SECRET_KEY"]
    token_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + API_KEY + "&client_secret=" + SECRET_KEY
    response = requests.get(token_url)
    try:
        global token
        token = response.json()["access_token"]
    except:
        if response.json()["error"] == "invalid_client":
            tkinter.messagebox.showwarning(title='警告', message='配置信息错误导致获取TOKEN失败，检查后重新填写！')
        elif response.json()["error"] == "invalid_request":
            tkinter.messagebox.showwarning(title='警告', message='API错误导致获取TOKEN失败，请检查软件更新！')
        else:
            tkinter.messagebox.showerror(title='错误', message='未知错误导致获取TOKEN失败，请联系开发者：\n邮箱：Voidmatrix@outlook.com')
        window.destroy()
        window.quit()


def synthetize(text, token, speed, pit, volume, person, aue, fname):
    text = quote(quote(text))
    cuid = hashlib.md5(token.encode()).hexdigest()
    data = "tex={}&tok={}&cuid={}&spd={}&pit={}&vol={}&per={}&aue={}&lan=zh&ctp=1".format(text, token, cuid, speed, pit,
                                                                                          volume, person, aue)
    response = requests.post('https://tsn.baidu.com/text2audio', data=data)
    if not response.headers['Content-Type'] == 'application/json':
        with open(fname, 'wb') as f:
            f.write(response.content)
        info_label['text'] = "• 当前状态：准备就绪..."
        tkinter.messagebox.showinfo(title='提示', message='语音合成成功，文件已保存！')
    else:
        tkinter.messagebox.showerror(title='错误', message='语音合成失败，错误信息：\n{}：{}'.format(response.json()["err_no"],
                                                                                      response.json()["err_msg"]))


bg_color = '#FAEBD7'
hightlight_color = 'Orange'

window = tk.Tk()

window.title('百度智能云 - 语音合成助手 v1.0.1')
window['background'] = bg_color
window.geometry('740x360')
window.resizable(width=False, height=False)
window.iconbitmap("./icon.ico")

isTSCheckBtnSelected = tk.IntVar()
isTSCheckBtnSelected.set(1)
default_name = tk.StringVar()
default_name.set("YYYY-MM-DD HH.MM.SS")


def toggleTimeStampDisable():
    global isTSCheckBtnSelected
    if name_input['state'] == 'disabled':
        name_input['state'] = 'normal'
        isTSCheckBtnSelected = 0
    else:
        name_input['state'] = 'disabled'
        isTSCheckBtnSelected = 1


def onStart():
    global isTSCheckBtnSelected, token
    if token == "":
        tkinter.messagebox.showwarning(title='警告', message='请等待TOKEN获取完成后重试！')
        return
    if isTSCheckBtnSelected:
        fname = time.strftime('%Y-%m-%d %H.%M.%S', time.localtime(time.time()))
    else:
        fname = name_input.get().strip()
    text = text_input.get("0.0", "end").strip()
    if text == "":
        tkinter.messagebox.showwarning(title='警告', message='需要进行合成的文本内容不可为空！')
        return
    if len(text) >= 2048:
        tkinter.messagebox.showwarning(title='警告', message='单次合成的文本内容不得超过2048字！')
        return
    info_label['text'] = "• 当前状态：正在进行合成任务..."
    person_map = {'默认女声 - 度小美': 0, '默认男声 - 度小宇': 1, '情感合成 - 度逍遥': 3, '情感合成 - 度丫丫': 4, '精品音库 - 度博文': 106,
                  '精品音库 - 度小童': 110, '精品音库 - 度小萌': 111, '精品音库 - 度米朵': 103, '精品音库 - 度小娇': 5}
    aue_map = {'.MP3 (默认)': 3, '.PCM-8K': 5, '.PCM-16K(非自然发声人)': 4, '.WAV(非自然发声人)': 6}
    type_map = {3: '.mp3', 5: '.pcm', 4: '.pcm', 6: '.wav'}
    person = person_map[person_combobox.get()]
    aue = aue_map[type_combobox.get()]
    speed = int(speed_combobox.get()[0:2])
    volume = int(volume_combobox.get()[0:2])
    pit = int(pit_combobox.get()[0:2])
    full_name = fname + type_map[aue]
    _thread.start_new_thread(synthetize, (text, token, speed, pit, volume, person, aue, full_name))


def onExit():
    if tkinter.messagebox.askokcancel("退出", "是否保存当前文本?"):
        text = text_input.get("0.0", "end").strip()
        try:
            with open('./Text.txt', 'w', encoding='utf-8') as file:
                file.write(text)
        except:
            tkinter.messagebox.showerror(title='错误', message='保存文本失败！')
        window.destroy()
        window.quit()
    else:
        window.destroy()
        window.quit()


text_input = scrolledtext.ScrolledText(window, highlightcolor=hightlight_color, font=('楷体', 12), highlightthickness=1.5,
                                       wrap=tk.WORD)
text_input.insert(1.0, "欢迎使用百度智能语音合成助手！")

person_label = tk.Label(window, text="音源选择：", font=('方正姚体', 14), bg=bg_color)
person_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
person_combobox['value'] = (
    '默认女声 - 度小美', '默认男声 - 度小宇', '情感合成 - 度逍遥', '情感合成 - 度丫丫', '精品音库 - 度博文', '精品音库 - 度小童', '精品音库 - 度小萌', '精品音库 - 度米朵',
    '精品音库 - 度小娇')
person_combobox.current(0)

speed_label = tk.Label(window, text="语速：", font=('方正姚体', 14), bg=bg_color)
speed_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
speed_combobox['value'] = ('0', '1', '2', '3', '4', '5 - 正常', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15')
speed_combobox.current(5)

volume_label = tk.Label(window, text="音量：", font=('方正姚体', 14), bg=bg_color)
volume_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
volume_combobox['value'] = ('0', '1', '2', '3', '4', '5 - 正常', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15')
volume_combobox.current(5)

type_label = tk.Label(window, text="编码格式：", font=('方正姚体', 14), bg=bg_color)
type_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
type_combobox['value'] = ('.MP3 (默认)', '.PCM-8K', '.PCM-16K(非自然发声人)', '.WAV(非自然发声人)')
type_combobox.current(0)

pit_label = tk.Label(window, text="音调：", font=('方正姚体', 14), bg=bg_color)
pit_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
pit_combobox['value'] = ('0', '1', '2', '3', '4', '5 - 正常', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15')
pit_combobox.current(5)

lang_label = tk.Label(window, text="语言：", font=('方正姚体', 14), bg=bg_color)
lang_combobox = ttk.Combobox(window, font=('黑体', 12), state='readonly')
lang_combobox['value'] = ('中英混合')
lang_combobox.current(0)

name_label = tk.Label(window, text="文件名：", font=('方正姚体', 14), bg=bg_color)
name_input = tk.Entry(highlightcolor=hightlight_color, highlightthickness=1.5, font=('黑体', 13),
                      textvariable=default_name)
name_input['state'] = 'disabled'

timestamp_checkBtn = tk.Checkbutton(window, text='使用时间戳命名文件', variable=isTSCheckBtnSelected, font=('楷体', 13),
                                    bg=bg_color, onvalue=1, offvalue=0, command=toggleTimeStampDisable)

start_btn = tk.Button(window, text="开始合成", font=('楷体', 18), width=13, height=1, bg="#E6E6FA", command=onStart)
exit_btn = tk.Button(window, text="退出", font=('楷体', 18), width=8, height=1, bg="#FFDA89", command=onExit)

info_label = tk.Label(window, text="• 当前状态：正在检查网络连接...", font=('隶书', 14), fg='#00008B', bg=bg_color)

text_input.place(x=20, y=20, anchor='nw', width=400, height=300)
person_label.place(x=425, y=25, anchor='nw')
person_combobox.place(x=525, y=27, anchor='nw', width=200, height=26)
type_label.place(x=425, y=70, anchor='nw')
type_combobox.place(x=525, y=72, anchor='nw', width=200, height=26)
speed_label.place(x=425, y=115, anchor='nw')
speed_combobox.place(x=485, y=117, anchor='nw', width=90, height=26)
volume_label.place(x=575, y=115, anchor='nw')
volume_combobox.place(x=635, y=117, anchor='nw', width=90, height=26)
pit_label.place(x=425, y=160, anchor='nw')
pit_combobox.place(x=485, y=162, anchor='nw', width=90, height=26)
lang_label.place(x=575, y=160, anchor='nw')
lang_combobox.place(x=635, y=162, anchor='nw', width=90, height=26)
name_label.place(x=425, y=205, anchor='nw')
name_input.place(x=500, y=205, anchor='nw', width=225, height=32)
timestamp_checkBtn.place(x=480, y=250, anchor='nw')
start_btn.place(x=435, y=300, anchor='nw')
exit_btn.place(x=620, y=300, anchor='nw')
info_label.place(x=20, y=330, anchor='nw')


def checkOnline():
    try:
        html = requests.get("https://www.baidu.com/", timeout=5)
        info_label['text'] = "• 当前状态：准备就绪..."
    except:
        info_label['text'] = "• 当前状态：网络连接失败！"
        tkinter.messagebox.showwarning(title='警告', message='网络链接失败，请检查网络连接后重试！')
        window.destroy()
        window.quit()


window.protocol("WM_DELETE_WINDOW", onExit)

processConfigFile()
_thread.start_new_thread(checkOnline, ())
_thread.start_new_thread(getToken, (cfgData,))

window.mainloop()

from logging import getLogger
from sys import exit

import tkinter
from tkinter import ttk as ttk

from .service import service as service
from .entity import entity

class view():
    # 各種情報
    info = {
        'drive':'',
        'flag':False,
        'conditions':[
            {
                'type':'8mm, miniDV',
                'check':True,
                'time':'',
                'name':'',
            },
            {
                'type':'VHS',
                'check':False,
                'time':'',
                'name':'',
            },
        ]
    }

    def __init__(self) -> None:
        self.logger = getLogger(__name__)

        # サービスのインスタンス化
        srv = service()
        self.e = entity()

        # 前回条件のロード
        self.logger.info('load last condition')
        self.info['drive'] = self.e.get('drive')
        for i in range(2):
            self.info['conditions'][i]['type'] = self.e.get('type',i)
            self.info['conditions'][i]['time'] = self.e.get('time',i)
            self.info['conditions'][i]['check'] = self.e.get('check',i)
        # ウィンドウの作成
        self.logger.info('create a main window')
        self.win = tkinter.Tk()
        self.win.title('VHS Extractor')

        # サイズ設定(16:9想定)[width:height]
        # self.win_size = [400,230]
        self.win_size = [400,280]
        self.win.geometry("{0[0]}x{0[1]}+{0[2]}+{0[3]}".format(self.win_size + self.get_center_position()))

        # オブジェクトの定義
        label_drive = tkinter.Label(self.win, text='保存先ドライブ', justify='left')
        self.chk_box_state = [tkinter.BooleanVar(),tkinter.BooleanVar()]
        self.label_title = [tkinter.Label(self.win),tkinter.Label(self.win)]
        self.label_timer = [tkinter.Label(self.win),tkinter.Label(self.win)]
        self.entry_box = [tkinter.Entry(),tkinter.Entry()]
        self.entry_box_timer = [tkinter.Entry(),tkinter.Entry()]
        self.button_exe = tkinter.Button(self.win, text="実行", width=20, command=self.exe_app)
        for i in range(2):
            self.chk_box_state[i].set(self.info['conditions'][i]['check'])
            self.label_timer[i].config(text='録画時間（分）', justify='left', state=self.get_state(self.info['conditions'][i]['check']))
            self.entry_box_timer[i].insert(0, self.info['conditions'][i]['time'])
            self.entry_box_timer[i].config(state=self.get_state(self.info['conditions'][i]['check']))
            self.label_title[i].config(text='タイトル', justify='left', state=self.get_state(self.info['conditions'][i]['check']))
            self.entry_box[i].config(state=self.get_state(self.info['conditions'][i]['check']))
        
        # 画面構成（オブジェクトの位置を確定）
        pos = [0,0]
        label_drive.grid(row=pos[0], column=pos[1], padx= 10, pady= 10, sticky=tkinter.W)
        pos = [1,0]
        # 有効なドライブの一覧をサービスから取得してドロップダウンリストにセット
        drives = srv.get_drives()
        self.dropdown_box = ttk.Combobox(self.win, values=drives, width=5, state='disable' if len(drives) <= 1 else 'readonly')
        # 前回選択されていたドライブが含まれていたらそのドライブを初期表示する
        last_drive = self.e.get('drive')
        if last_drive in drives:
            self.dropdown_box.current(drives.index(last_drive))
        else:
            self.dropdown_box.current(0)
        self.dropdown_box.grid(row=pos[0], column=pos[1], padx= 10, sticky=tkinter.W)

        # １列目
        pos = [2,0]
        chkbox = tkinter.Checkbutton(self.win, text=self.info['conditions'][0]['type'], variable=self.chk_box_state[0], command=lambda: self.change_state(int(0),self.chk_box_state[0].get()))
        chkbox.grid(row=pos[0], column=pos[1], padx=10, pady= (20,0), sticky=tkinter.W)
        pos = [3,0]
        self.label_timer[0].grid(row=pos[0], column=pos[1], padx= 5, sticky=tkinter.W)
        pos = [4,0]
        self.entry_box_timer[0].grid(row=pos[0], column=pos[1], padx= 10, sticky=tkinter.W)
        pos = [5,0]
        self.label_title[0].grid(row=pos[0], column=pos[1], padx= 5, sticky=tkinter.W)
        pos = [6,0]
        self.entry_box[0].grid(row=pos[0], column=pos[1], padx= 10, sticky=tkinter.W)

        # ２列目
        pos = [2,1]
        chkbox = tkinter.Checkbutton(self.win, text=self.info['conditions'][1]['type'], variable=self.chk_box_state[1], command=lambda: self.change_state(int(1), self.chk_box_state[1].get()))
        chkbox.grid(row=pos[0], column=pos[1], padx=(10,0), pady= (20,0), sticky=tkinter.W)
        pos = [3,1]
        self.label_timer[1].grid(row=pos[0], column=pos[1], padx= 5, sticky=tkinter.W)
        pos = [4,1]
        self.entry_box_timer[1].grid(row=pos[0], column=pos[1], padx= (10,0), sticky=tkinter.W)
        pos = [5,1]
        self.label_title[1].grid(row=pos[0], column=pos[1], padx= 5, sticky=tkinter.W)
        pos = [6,1]
        self.entry_box[1].grid(row=pos[0], column=pos[1], padx= (10,0), sticky=tkinter.W)

        # 実行ボタン
        pos = [7,0]
        self.button_exe.grid(row=pos[0], column=pos[1], padx=5, pady= 15, sticky=tkinter.W)

        # ウィンドウのループ処理
        self.win.mainloop()

        # ウィンドウが閉じた際のチェック処理
        if self.info['flag'] == False:
            self.logger.info('exit without recording')
            exit()
        self.logger.info('start recording')

    # ウィンドウが中心に配置される座標を取得
    def get_center_position(self):
        def calc(a,b): return int((a-b)/2)
        w = calc(self.win.winfo_screenwidth(), self.win_size[0])
        h = calc(self.win.winfo_screenheight(), self.win_size[1])
        return [w,h]

    # boolから文字列を取得
    def get_state(self, bool:bool) -> str:
        return 'normal' if bool else 'disabled'

    # チェックボタン押下時処理
    def change_state(self, num:int,bool:bool):
        self.label_timer[num].config(state=self.get_state(bool))
        self.entry_box_timer[num].config(state=self.get_state(bool))
        self.label_title[num].config(state=self.get_state(bool))
        self.entry_box[num].config(state=self.get_state(bool))
        self.button_exe.config(state=self.get_state(self.chk_box_state[0].get() or self.chk_box_state[1].get()))

    # イベント処理
    def exe_app(self):
        self.logger.info('exe button was pressed')
        self.info['flag'] = True
        # infoとエンティティに格納
        self.info['drive'] = self.dropdown_box.get()
        self.e.set('drive', self.dropdown_box.get())
        for i in range(2):
            self.info['conditions'][i]['time'] = self.entry_box_timer[i].get()
            self.info['conditions'][i]['name'] = self.entry_box[i].get()
            self.info['conditions'][i]['check'] = self.chk_box_state[i].get()
            self.e.set('type', self.info['conditions'][i]['type'], i)
            self.e.set('time', self.info['conditions'][i]['time'], i)
            self.e.set('check', self.info['conditions'][i]['check'], i)
        self.e.close()
        self.logger.info('save infomation. '
                            +'drive :"'+self.info['drive']+'", '
                            +'type_1:"'+self.info['conditions'][0]['type']+'", '
                            +'time_1:"'+self.info['conditions'][0]['time']+'", '
                            +'check_1:'+str(self.info['conditions'][0]['check'])+', '
                            +'type_2:"'+self.info['conditions'][1]['type']+'", '
                            +'time_2:"'+self.info['conditions'][1]['time']+'", '
                            +'check_2:'+str(self.info['conditions'][1]['check'])
                        )

        # ウィンドウを閉じる
        self.win.quit()


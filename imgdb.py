import sqlite3

class ImageDatabase:

    def __init__(self, sq_path) -> None:
        self.db_path = sq_path
        with sqlite3.connect(sq_path) as conn:
            sql_cmd = '''CREATE TABLE IF NOT EXISTS images(
                id          INT     NOT NULL    PRIMARY KEY,
                url         TEXT    NOT NULL,
                des         TEXT,
                err_times   INT     NOT NULL    DEFAULT 0
            );'''
            conn.execute(sql_cmd)

    def insert_url(self, url: str, des: str) -> None:
        ''' 插入数据 '''
        # 向数据库中插入数据
        try:
            with sqlite3.connect(self.db_path) as conn:
                img_id = conn.execute('''SELECT MAX(id) FROM images;''').fetchone()[0]
                if img_id:
                    img_id = img_id + 1
                else:
                    img_id = 1
                sql_cmd = '''INSERT INTO images(id, url, des) VALUES(?, ?, ?);'''
                conn.execute(sql_cmd, (img_id, url, des))
        except Exception as e:
            print(f"Data insert error {e}")

    def random_url(self, num = 1) -> str | None:
        ''' 随机返回一条数据库中保存的 url '''
        url = None
        try :
            with sqlite3.connect(self.db_path) as conn:
                sql_cmd = '''SELECT url FROM images ORDER BY RANDOM() LIMIT {};'''.format(num)
                sel_data = conn.execute(sql_cmd).fetchone()
        except Exception as e:
            print(e)
        else:
            if sel_data:
                url = sel_data[0]
            else:
                print('No data in database')

        return url

    def delete_url(self, url: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                sql_cmd = '''DELETE FROM images WHERE url = '{}';'''.format(url)
                conn.execute(sql_cmd)
        except Exception as e:
            print(e)

    def error_url(self, url: str) -> None:
        ''' 设置错误次数 '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 将错误数量读出来
                sql_cmd = '''SELECT err_times FROM images WHERE url = '{}';'''.format(url)
                f = conn.execute(sql_cmd).fetchone()
                if not f:
                   raise ValueError(f'Url: {url} not fount in database')

                err_times = f[0]
                if err_times >= 3:
                    # 错误次数大于 3 次则删除
                    self.delete_url(url)
                    return 0

                sql_cmd = '''UPDATE images SET err_times = err_times + 1 WHERE url = '{}';'''.format(url)
                conn.execute(sql_cmd)

        except Exception as e:
            print(e)

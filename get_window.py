import win32gui


class GetWindow:
    def __init__(self):
        self._titles = set()
        self.title_list = self._find_window()

    def _get_titles(self, hwnd, m):
        if win32gui.IsWindow(hwnd) and \
                win32gui.IsWindowEnabled(hwnd) and \
                win32gui.IsWindowVisible(hwnd):
            self._titles.add(win32gui.GetWindowText(hwnd))

    def _find_window(self):
        win32gui.EnumWindows(self._get_titles, 0)
        return [t for t in self._titles if t]


if __name__ == '__main__':

    gw = GetWindow()
    for t in gw.title_list:
        print(t)



from direct.showbase.ShowBase import ShowBase
from panda3d.core import LPoint3f
from random import randint, random
import pickle
from block import Block

# Функция получения случайного цвета
def getRandomColor():
    return (random()*0.3+0.7,
            random()*0.3+0.7,
            random()*0.3+0.7, 1)

# Функция получения цвета выделения для заданного цвета блока
def getSelectColor(color):
    # если цвет не определён
    if color is None:
        return (0.15, 0.15, 0.15, 0.9)
    else:
        return (color[0]*0.4,
                color[1]*0.4,
                color[2]*0.4, 0.9)


# Класс менеджера карты
class MapManager():
    # Конструктор
    def __init__(self):
        # список с блоками
        self.blocks = list()
        # выделенный блок
        self.selected_block = None
        # текущий цвет для новых блоков
        self.color = None
        # получаем текущий цвет выделения
        self.selected_color = getSelectColor(self.color)

    # Метод добавления нового блока цвета color в позицию position
    def addBlock(self, position, color=None):
        # проверяем, есть ли в этой позиции другой блок
        for block in self.blocks:
            # если есть - выходим
            if block.getPos() == position:
                return

        # если цвет не задан
        if color is None:
            # если текущий цвет не задан
            if self.color is None:
                # генерируем случайный цвет
                color = getRandomColor()
            else:
                # устанавливаем текущий цвет
                color = self.color

        # создаём блок
        block = Block(position, color)
        # добавляем его в список
        self.blocks.append(block)

    # Метод установки текущего цвета для новых блоков
    def setColor(self, color):
        self.color = color
        # получаем текущий цвет выделения
        self.selected_color = getSelectColor(self.color)

        # если есть выделенный блок
        if self.selected_block:
            # обновляем его цвет
            self.selected_block.updateColor(self.selected_color)

    # Метод создания базовой карты - квадрата
    def basicMap(self):
        # удаляем все блоки
        self.clearAll()

        for i in range(-7,8):
            for j in range(-7,8):
                pos = (i, j, -2)
                self.addBlock(pos, (1,1,1,1))

    # Метод генерации новой случайной карты
    def generateRandomMap(self):
        # удаляем все блоки
        self.clearAll()

        # Блоки в нижней части карты
        for i in range(-8,9):
            for j in range(-8,9):
                pos = (i, j, randint(-4,-2))
                self.addBlock(pos)

        # Блоки по краям карты
        for i in range(-8,9):
            for j in range(-8,9):
                if -5 < i < 5 and -5 < j < 5:
                    continue
                pos = (i, j, randint(-1,6))
                self.addBlock(pos)

    # Метод создания карты, аргументы
    # colors - словарь цветов,
    #   ключ - символ цвета,
    #   значение - цвет
    # matrix - трёхмерный вложенный список цветов
    #   значения - символы цвета
    # shift - сдвиг всех координат
    def createMap(self, colors, matrix, shift):
        # удаляем все блоки
        self.clearAll()

        # проходимся по всем трём координатам
        for z in range(len(matrix)):
            for y in range(len(matrix[z])):
                for x in range(len(matrix[z][y])):
                    # Получаем цвет блока
                    key = matrix[z][y][x]
                    # если такой цвет есть в словаре цветов
                    if key in colors and colors[key]:
                        # Рассчитываем позицию
                        # Координата Y инвертируется !!!
                        pos = (x + shift[0],
                               - y - shift[1],
                               z + shift[2])
                        # добавляем новый блок
                        self.addBlock(pos, colors[key])

    # Метод снятия выделения со всех блоков
    def deselectAllBlocks(self):
        for block in self.blocks:
            block.setSelected(False)

    # Метод выбора блока по заданному ключу блока
    def selectBlock(self, key):
        # сбрасываем текущий выделенный блок
        self.selected_block = None

        for block in self.blocks:
            # если ключ совпал
            if block.getKey() == key:
                # устанавливаем новый выделенный блок
                self.selected_block = block
                # устанавливаем в нём флаг и цвет выделения
                block.setSelected(True, self.selected_color)
            else:
                # сбрасываем выделение на этом блоке
                block.setSelected(False)

        # если выделенный блок найден
        if self.selected_block:
            # возвращаем его узел
            return self.selected_block.getNode()
        else:
            return None

    # Метод удаления выделенного блока
    def deleteSelectedBlock(self):
        # если есть выделенный блок
        if self.selected_block:
            # сбрасываем текущий выделенный блок
            self.selected_block = None

            # ищем выделенный узел в списке
            for i in range(len(self.blocks)):
                if self.blocks[i].getSelected():
                    # удаляем его из Panda3D
                    self.blocks[i].remove()
                    # удаляем его из памяти
                    del self.blocks[i]
                    # прерываем цикл
                    break

    # Метод очистки карты - удаления всех блоков
    def clearAll(self):
        # сбрасываем текущий выделенный блок
        self.selected_block = None

        # удаляем блоки из Panda3D
        for block in self.blocks:
            block.remove()

        # удаляем блоки из памяти
        self.blocks.clear()

    # Метод сохранения карты в файл
    # filename - имя файла
    def saveMap(self, filename):
        # если нет блоков
        if not self.blocks:
            return

        # открываем бинарный файл на запись
        fout = open(filename, 'wb')

        # сохраняем в начало файла количество блоков
        pickle.dump(len(self.blocks), fout)

        # обходим все блоки
        for block in self.blocks:
            # сохраняем позицию
            pickle.dump(block.getPos(), fout)
            # сохраняем цвет
            pickle.dump(block.getColor(), fout)

        # закрываем файл
        fout.close()

        print("save map to", filename)

    # Метод загрузки карты из файла
    # filename - имя файла
    def loadMap(self, filename):
        # удаляем все блоки
        self.clearAll()

        # открываем бинарный файл на чтение
        fin = open(filename, 'rb')

        # считываем количество блоков
        lenght = pickle.load(fin)

        for i in range(lenght):
            # считываем позицию
            pos = pickle.load(fin)
            # считываем цвет
            color = pickle.load(fin)

            # создаём новый блок
            self.addBlock(pos, color)

        # закрываем файл
        fin.close()

        print("load map from", filename)


if __name__ == '__main__':
    # отладка модуля
    from direct.showbase.ShowBase import ShowBase
    from controller import Controller

    class MyApp(ShowBase):

        def __init__(self):
            ShowBase.__init__(self)

            self.controller = Controller()

            self.map_manager = MapManager()

            self.accept('f1', self.map_manager.basicMap)
            self.accept('f2', self.map_manager.generateRandomMap)
            self.accept('f3', self.map_manager.saveMap, ["testmap.dat"])
            self.accept('f4', self.map_manager.loadMap, ["testmap.dat"])
            self.accept('f5', self.createMap)

            print("'f1' - создать базовую карту")
            print("'f2' - создать случайную карту")
            print("'f3' - сохранить карту")
            print("'f4' - загрузить карту")
            print("'f5' - создать карту по вложенному списку")

            self.map_manager.generateRandomMap()

        def createMap(self):
            # словарь цветовых обозначений блоков
            colors = {'R':(1.0, 0, 0, 1),
                      'G':(0, 1.0, 0, 0.5),
                      'B':(0, 0, 1.0, 0.5),
                      'Y':(1.0, 1.0, 0, 1),
                      'O':(1.0, 0.5, 0.0, 1),
                      'W':(1.0, 1.0, 1.0, 1),
                      '-':None}

            # вложенный список блоков
            blocks = [
                [['G','O','O','O','G'],
                 ['O','-','-','-','O'],
                 ['O','-','W','-','O'],
                 ['O','-','-','-','O'],
                 ['G','O','O','O','G']],

                [['G','-','-','-','G'],
                 ['-','-','-','-','-'],
                 ['-','-','W','-','-'],
                 ['-','-','-','-','-'],
                 ['G','-','-','-','G']],

                [['G','-','R','-','G'],
                 ['-','-','R','-','-'],
                 ['R','R','W','R','R'],
                 ['-','-','R','-','-'],
                 ['G','-','R','-','G']],

                [['G','-','-','-','G'],
                 ['-','-','-','-','-'],
                 ['-','-','W','-','-'],
                 ['-','-','-','-','-'],
                 ['G','-','-','-','G']],

                [['G','Y','Y','Y','G'],
                 ['Y','-','-','-','Y'],
                 ['Y','-','W','-','Y'],
                 ['Y','-','-','-','Y'],
                 ['G','Y','Y','Y','G']],
                ]

            self.map_manager.createMap(colors, blocks, (-2,-10,-2))


    app = MyApp()
    app.run()

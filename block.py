from panda3d.core import Texture, TextureStage
from panda3d.core import BitMask32
from panda3d.core import TransparencyAttrib


# Класс элемента строительного блока
class Block():
    # свойство класса - текущий индекс объекта
    current_index = 0

    # Конструктор блока. Аргументы:
    #  position - позиция блока на сцене
    #  color - цвет заливки
    def __init__(self, position=(0, 0, 0), color=(1, 1, 1, 1)):
        # получаем уникальный ключ объекта - текущий индекс
        self.key = str(Block.current_index)
        # увеличиваем индекс
        Block.current_index += 1
        # флаг выделенного блока
        self.selected = False
        # загружаем модель блока
        self.block = loader.loadModel('block')
        # и текстуру к ней
        tex = loader.loadTexture('block.png')
        # устанавливаем текстуру на модель
        self.block.setTexture(tex)
        # устанавливаем учёт прозрачности цвета
        self.block.setTransparency(TransparencyAttrib.MAlpha)
        # перемещение модели в рендер, смена родителя
        self.block.reparentTo(render)
        # устанавливаем позицию модели
        self.block.setPos(position)
        # устанавливаем цвет модели
        self.color = color
        self.block.setColor(self.color)

        # настраиваем объект для определения выделения
        # вместе с моделью загружается и геометрия столкновения
        # ищем узел геометрии столкновения
        collisionNode = self.block.find("*").node()
        # устанавливаем такую же маску ДО как и у луча выделения
        collisionNode.setIntoCollideMask(BitMask32.bit(1))
        # устанавливаем тег, чтобы потом определить что именно мы выделили
        collisionNode.setTag('key', self.key)

    # Метод получения ключа блока
    def getKey(self):
        return self.key

    # Метод получения цвета
    def getColor(self):
        return self.color

    # Метод получения позиции блока
    def getPos(self):
        return self.block.getPos()

    # Метод получения узла с блоком
    def getNode(self):
        return self.block

    # Метод установки выделения на блок
    def setSelected(self, selected, color = (0, 0, 1, 1)):
        # если изменился статус выделения
        if self.selected != selected:
            # сохраняем новый статус
            self.selected = selected
            if self.selected:
                # устанавливаем цвет выделения
                self.block.setColor(color)
            else:
                # устанавливаем оригинальный цвет
                self.block.setColor(self.color)

    # Метод обновления цвета блока
    def updateColor(self, color):
        self.block.setColor(color)

    # Метод получения статуса выделения
    def getSelected(self):
        return self.selected

    # Метод удаления объекта блока из Panda3D
    def remove(self):
        self.block.removeNode()


if __name__ == '__main__':
    # отладка модуля
    from direct.showbase.ShowBase import ShowBase

    class MyApp(ShowBase):

        def __init__(self):
            ShowBase.__init__(self)

            b1 = Block((0,10,0), (0.5,1,0.5,0.2))
            b2 = Block((1,10,0), (1,1,0.5,1))
            b3 = Block((0,10,2), (0.5,1,1,1))
            b4 = Block((-2,15,-2), (1,0.5,1,1))

    app = MyApp()
    app.run()



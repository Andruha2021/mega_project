from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import BitMask32
from panda3d.core import LPoint3f
from mapmanager import MapManager


# Класс редактора блоков
class Editor(DirectObject):
    # Конструктор
    def __init__(self, map_manager):
        # сохраняем ссылку на объект менеджера карты
        self.map_manager = map_manager

        # режим редактирования
        self.edit_mode = True

        # создание обходчика столкновений
        self.traverser = CollisionTraverser()
        # очередь обработки столкновений
        self.collisQueue = CollisionHandlerQueue()
        # узел для луча столкновений
        collisionNode = CollisionNode('centerRay')
        # устанавливаем маску проверки столкновений ОТ
        collisionNode.setFromCollideMask(BitMask32.bit(1))
        # сбрасываем маску проверки столкновений ДО
        collisionNode.setIntoCollideMask(BitMask32.allOff())
        # создаём луч
        self.collisRay = CollisionRay()
        # и прикрепляем к созданному ранее узлу
        collisionNode.addSolid(self.collisRay)
        # закрепляем узел на камере
        collisCamNode = base.camera.attachNewNode(collisionNode)
        # уведомляем обходчик о новом «объекте ОТ»
        self.traverser.addCollider(collisCamNode, self.collisQueue)
        # визуализируем столкновения (раскомментировать/закоментировать)
        #self.traverser.showCollisions(base.render)
        # позиция для добавления нового блока
        self.new_position = None
        # ключ выделенного блока
        self.selected_key = None
        # узел выделенного блока
        self.selected_node = None

        # запускаем задачу проверки выделения блоков
        taskMgr.doMethodLater(0.02, self.testBlocksSelection,
                              "test_block-task")

        # регистрируем на нажатие левой кнопки мыши
        # событие добавления блока
        self.accept('mouse1', self.addBlock)
        # регистрируем на нажатие правой кнопки мыши
        # событие удаления блока
        self.accept('mouse3', self.delBlock)

    #метод установки режима редактирования
    def setEditMode(self, mode):
        self.edit_mode = mode
        if self.edit_mode:
            # сбрасываем выделение
            self.resetSelectedBlock()
            # запускаем задачу проверки выделения блоков
            taskMgr.doMethodLater(0.02, self.testBlocksSelection,
                                  "test_block-task")
        else:
            # удаляем задачу проверки выделения блоков
            taskMgr.remove("test_block-task")
            # снимаем выделение со всех блоков
            self.map_manager.deselectAllBlocks()

    # Метод сброса свойств выделенного блока
    def resetSelectedBlock(self):
        self.new_position = None
        self.selected_key = None
        self.selected_node = None

    # Метод добавления блока
    def addBlock(self):
        # если есть позиция для нового блока
        if self.new_position:
            # добавляем блок в эту позицию
            self.map_manager.addBlock(self.new_position)
            # сбрасываем выделение
            self.resetSelectedBlock()

    # Метод удаления блока
    def delBlock(self):
        # удаляем выделенный блок
        self.map_manager.deleteSelectedBlock()
        # сбрасываем выделение
        self.resetSelectedBlock()

    # Метод проверки проверки выделения блоков
    def testBlocksSelection(self, task):
        # устанавливаем позицию луча столкновений в центр экрана
        self.collisRay.setFromLens(base.camNode, 0, 0)
        # запускаем обходчик на проверку
        self.traverser.traverse(base.render)

        # если обходчик обнаружил какие-то столкновения
        if self.collisQueue.getNumEntries() > 0:
            # сортируем их, чтобы получить ближайшее
            self.collisQueue.sortEntries()
            # получаем описание ближайшего столкновения
            collisionEntry = self.collisQueue.getEntry(0)
            # получаем узел с «объектом ДО» и ключ выделенного блока
            key = collisionEntry.getIntoNodePath().getTag('key')

            # если найден новый блок
            if key != self.selected_key:
                # обновляем ключ выделенного блока
                self.selected_key = key
                # выделяем новый блок
                self.selected_node = self.map_manager.selectBlock(key)

            # если есть выделенный блок
            if self.selected_node:
                # координаты выделенного блока
                selected_position = self.selected_node.getPos()
                # вектор нормали к поверхности на выделенном блоке
                normal = collisionEntry.getSurfaceNormal(self.selected_node)
                # позиция для добавления нового блока
                self.new_position = selected_position + normal
        else:
            # снимаем выделение со всех блоков
            self.map_manager.deselectAllBlocks()
            # сбрасываем выделение
            self.resetSelectedBlock()

        # сообщаем о необходимости повторного запуска задачи
        return task.again

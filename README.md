# Python国际象棋游戏

这是一个使用Python和Pygame开发的国际象棋游戏，提供了完整的国际象棋规则实现和图形用户界面。

## 功能特点

- 完整的国际象棋规则实现
  - 所有棋子的标准移动规则
  - 特殊规则：王车易位、吃过路兵、兵升变
  - 将军和将死检测
  - 合法移动检查
- 现代化的图形界面
  - 美观的棋盘和棋子设计
  - 棋子选中高亮显示
  - 可能移动位置提示
  - 兵升变选择菜单
- 用户友好的操作方式
  - 鼠标点击操作
  - 直观的移动提示
  - 清晰的游戏状态显示

## 安装说明

1. 确保已安装Python 3.x
2. 安装必要的依赖：
   ```bash
   pip install pygame
   ```
3. 下载项目文件

## 使用方法

1. 运行游戏：
   ```bash
   python chess_game.py
   ```

2. 游戏操作：
   - 点击选择棋子
   - 点击高亮格子移动棋子
   - 当兵到达对方底线时，点击升变菜单选择升变棋子
   - 关闭窗口结束游戏

## 游戏规则

- 白方先行
- 遵循标准国际象棋规则
- 支持所有特殊规则：
  - 王车易位（长易位和短易位）
  - 吃过路兵
  - 兵升变
  - 将军和将死判定

## 项目结构

- `chess_game.py`: 主程序文件，包含：
  - `PieceColor`和`PieceType`枚举类：定义棋子颜色和类型
  - `Piece`类：棋子类，实现棋子的基本属性和移动规则
  - `ChessGame`类：游戏主类，实现游戏逻辑和界面绘制

## 技术特点

- 使用Pygame进行图形界面开发
- 面向对象的程序设计
- 模块化的代码结构
- 完整的游戏状态管理
- 高效的移动验证算法
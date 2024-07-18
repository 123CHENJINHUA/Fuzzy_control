import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import matplotlib.pyplot as plt



def fuzzy_control(pressure_value,pressure_rate_value):

    pressure_range = np.arange(0, 80.1, 0.1, np.float32)
    pressure_rate_range = np.arange(-12, 65.1, 0.1, np.float32)
    speed_range = np.arange(0, 51, 1, np.float32)

    # 创建模糊控制变量
    pressure = ctrl.Antecedent(pressure_range, 'pressure')
    pressure_rate = ctrl.Antecedent(pressure_rate_range, 'pressure_rate')
    speed = ctrl.Consequent(speed_range, 'speed')

    # 定义模糊集和其隶属度函数
    pressure['VL'] = fuzz.trapmf(pressure_range, [0, 0, 20, 23])
    pressure['L'] = fuzz.trimf(pressure_range, [20, 23, 26])
    pressure['M'] = fuzz.trimf(pressure_range, [23, 26, 30])
    pressure['H'] = fuzz.trimf(pressure_range, [26, 30, 36])
    pressure['VH'] = fuzz.trimf(pressure_range, [30, 36, 50])

    pressure_rate['FL'] = fuzz.trapmf(pressure_rate_range, [-20, -20, -8, -4])
    pressure_rate['SL'] = fuzz.trimf(pressure_rate_range, [-8, -4, 0])
    pressure_rate['SS'] = fuzz.trimf(pressure_rate_range, [-4, 0, 25])
    pressure_rate['FS'] = fuzz.trimf(pressure_rate_range, [0, 50, 65])
    pressure_rate['VFS'] = fuzz.trimf(pressure_rate_range, [50, 65, 65])

    speed['VS'] = fuzz.trapmf(speed_range, [0,0,0,0])
    speed['S'] = fuzz.trimf(speed_range, [24, 25, 28])
    speed['M'] = fuzz.trimf(speed_range, [25, 28, 31])
    speed['F'] = fuzz.trimf(speed_range, [28, 31, 36])
    speed['VF'] = fuzz.trimf(speed_range, [31, 36, 45])

    # pressure.view()
    # pressure_rate.view()
    # speed.view()

    # 设定输出powder的解模糊方法——质心解模糊方式
    speed.defuzzify_method = 'centroid'

    # 输出为VS的规则
    rule0 = ctrl.Rule(antecedent=((pressure['VH'] & pressure_rate['VFS']) |
                              (pressure['VH'] & pressure_rate['FS']) |
                              (pressure['VH'] & pressure_rate['SL']) |
                              (pressure['VH'] & pressure_rate['SS']) |
                              (pressure['VH'] & pressure_rate['FL']) |
                              (pressure['H'] & pressure_rate['SS']) |
                              (pressure['H'] & pressure_rate['FS']) |
                              (pressure['H'] & pressure_rate['SS']) |
                              (pressure['H'] & pressure_rate['VFS'])),
                  consequent=speed['VS'], label='rule VS')
    # 输出为VF的规则
    rule4 = ctrl.Rule(antecedent=((pressure['L'] & pressure_rate['FL']) |
                                (pressure['VL'] & pressure_rate['FL']) |
                                (pressure['VL'] & pressure_rate['SL'])),
                    consequent=speed['VF'], label='rule VF')

    # 输出为S的规则
    rule1 = ctrl.Rule(antecedent=(
                                
                                (pressure['M'] & pressure_rate['SS']) |
                                (pressure['VL'] & pressure_rate['VFS']) |

                                (pressure['M'] & pressure_rate['FS']) |
                                (pressure['M'] & pressure_rate['VFS'])
                                ),
                    consequent=speed['S'], label='rule S')

    # 输出为M的规则
    rule2 = ctrl.Rule(antecedent=((pressure['H'] & pressure_rate['FL']) |
                                (pressure['M'] & pressure_rate['FL']) |
                                (pressure['M'] & pressure_rate['SL']) |
                                (pressure['L'] & pressure_rate['VFS']) ),
                    consequent=speed['M'], label='rule M')

    # 输出为F的规则
    rule3 = ctrl.Rule(antecedent=(
                                (pressure['L'] & pressure_rate['SL']) |
                                (pressure['L'] & pressure_rate['SS']) |
                                (pressure['VL'] & pressure_rate['SS']) |
                                (pressure['VL'] & pressure_rate['FS']) |

                                (pressure['L'] & pressure_rate['FS'])),
                    consequent=speed['F'], label='rule F')

    # 系统和运行环境初始化
    system = ctrl.ControlSystem(rules=[rule0, rule1, rule2, rule3, rule4])
    sim = ctrl.ControlSystemSimulation(system)


    sim.input['pressure'] = pressure_value
    sim.input['pressure_rate'] = pressure_rate_value
    sim.compute()   # 运行系统
    output_speed = sim.output['speed']

    # # show figure
    # speed.view(sim=sim)
    # plt.show()

    return output_speed


if __name__ == "__main__":

    pressure = 20
    pressure_rate = 7
    output_speed = fuzzy_control(pressure,pressure_rate)
    # 打印输出结果
    print(output_speed)
    
    
    
cmake_minimum_required(VERSION 3.8)
project(innex_teleop)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_joy_teleop test/test_joy_teleop.py TIMEOUT 120)
endif()

ament_package()

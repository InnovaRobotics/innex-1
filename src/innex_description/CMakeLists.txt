cmake_minimum_required(VERSION 3.8)
project(innex_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch urdf
    DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_urdf test/test_urdf.py TIMEOUT 120)
endif()

ament_package()

cmake_minimum_required(VERSION 3.8)
project(innex_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch worlds models
  DESTINATION share/${PROJECT_NAME}
)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/innex_sim.dsv.in")

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_models test/test_models.py TIMEOUT 120)
  ament_add_pytest_test(test_worlds test/test_worlds.py TIMEOUT 300)
  ament_add_pytest_test(test_meshes test/test_meshes.py TIMEOUT 120)
endif()

ament_package()

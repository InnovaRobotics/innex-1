cmake_minimum_required(VERSION 3.8)
project(innex_sim)

find_package(ament_cmake REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(MESH_DIR ${CMAKE_CURRENT_BINARY_DIR}/models)
# List the generated files so CMake knows when to rerun the script.
set(MESH_OUTPUTS
  ${MESH_DIR}/moon_yard_terrain/meshes/terrain.obj
  ${MESH_DIR}/rock_a/meshes/rock.obj
  ${MESH_DIR}/rock_b/meshes/rock.obj
  ${MESH_DIR}/rock_c/meshes/rock.obj
  ${MESH_DIR}/rock_d/meshes/rock.obj
)

add_custom_command(
  OUTPUT ${MESH_OUTPUTS}
  COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_assets.py
    --output-dir ${MESH_DIR}
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_assets.py
  COMMENT "Generating the Moon Yard meshes"
)
add_custom_target(innex_sim_meshes ALL DEPENDS ${MESH_OUTPUTS})

install(DIRECTORY config launch worlds models
  DESTINATION share/${PROJECT_NAME}
)
install(DIRECTORY ${MESH_DIR}/
  DESTINATION share/${PROJECT_NAME}/models
)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/innex_sim.dsv.in")

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_models test/test_models.py TIMEOUT 120)
  ament_add_pytest_test(test_worlds test/test_worlds.py TIMEOUT 300)
  ament_add_pytest_test(test_meshes test/test_meshes.py TIMEOUT 120)
endif()

ament_package()

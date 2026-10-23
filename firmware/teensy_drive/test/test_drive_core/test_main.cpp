#include <unity.h>
#include <DriveCore.h>
#include <cstring>

using drive::Core;
bool send(Core& core, uint32_t seq, int32_t left, int32_t right, uint32_t now) {
    uint8_t frame[drive::kFrameSize];
    drive::encode({seq, left, right}, frame);
    bool accepted = false;
    for (uint8_t byte : frame) accepted = core.receive(byte, now);
    return accepted;
}
void setUp() {}
void tearDown() {}

void test_startup_requires_zero() {
    Core c;
    TEST_ASSERT_FALSE(c.armed());
    TEST_ASSERT_EQUAL_INT32(0, c.left());
    TEST_ASSERT_FALSE(send(c, 1, 300, 300, 0));
    TEST_ASSERT_TRUE(send(c, 2, 0, 0, 1));
    TEST_ASSERT_TRUE(send(c, 3, -300, 400, 2));
    TEST_ASSERT_EQUAL_INT32(-300, c.left());
    TEST_ASSERT_EQUAL_INT32(400, c.right());
}
void test_timeout_boundary_and_rearm() {
    Core c;
    send(c, 1, 0, 0, 0); send(c, 2, 500, 500, 10);
    c.tick(259); TEST_ASSERT_EQUAL_INT32(500, c.left());
    c.tick(260); TEST_ASSERT_FALSE(c.armed());
    TEST_ASSERT_EQUAL_INT32(0, c.left()); TEST_ASSERT_EQUAL_INT32(0, c.right());
    TEST_ASSERT_FALSE(send(c, 3, 500, 500, 261));
    TEST_ASSERT_TRUE(send(c, 4, 0, 0, 262));
    TEST_ASSERT_TRUE(send(c, 5, 300, 300, 263));
}
void test_old_duplicate_and_ambiguous_do_not_refresh() {
    Core c;
    send(c, 10, 0, 0, 0); send(c, 11, 200, 400, 1);
    TEST_ASSERT_FALSE(send(c, 10, -200, -200, 100));
    TEST_ASSERT_FALSE(send(c, 11, -200, -200, 200));
    TEST_ASSERT_FALSE(send(c, 11U + 0x80000000U, 0, 0, 220));
    TEST_ASSERT_EQUAL_INT32(200, c.left());
    c.tick(251); TEST_ASSERT_FALSE(c.armed());
}
void test_sequence_and_clock_wrap() {
    Core c;
    send(c, 0xfffffffeU, 0, 0, 0xfffffff0U);
    TEST_ASSERT_TRUE(send(c, 0xffffffffU, 100, -100, 0xfffffff5U));
    TEST_ASSERT_TRUE(send(c, 0, 200, -200, 0xfffffff6U));
    c.tick(239); TEST_ASSERT_TRUE(c.armed());
    c.tick(240); TEST_ASSERT_FALSE(c.armed());
}
void test_bad_crc_stops_and_resynchronises() {
    Core c;
    send(c, 1, 0, 0, 0); send(c, 2, 200, 200, 1);
    uint8_t frame[drive::kFrameSize]; drive::encode({3, 400, 400}, frame);
    frame[8] ^= 1;
    for (auto byte : frame) c.receive(byte, 10);
    TEST_ASSERT_FALSE(c.armed());
    TEST_ASSERT_FALSE(send(c, 4, 100, 100, 11));
    TEST_ASSERT_TRUE(send(c, 5, 0, 0, 12));
    TEST_ASSERT_TRUE(send(c, 6, 200, 200, 13));
}
void test_split_frame_and_partial_expiry() {
    Core c; uint8_t frame[drive::kFrameSize]; drive::encode({1, 0, 0}, frame);
    for (unsigned i = 0; i < 9; ++i) c.receive(frame[i], 0);
    TEST_ASSERT_FALSE(c.armed());
    for (unsigned i = 9; i < 18; ++i) c.receive(frame[i], 20);
    TEST_ASSERT_TRUE(c.armed());
    c.disconnect();
    drive::encode({2, 0, 0}, frame);
    for (unsigned i = 0; i < 9; ++i) c.receive(frame[i], 30);
    for (unsigned i = 9; i < 18; ++i) c.receive(frame[i], 280);
    TEST_ASSERT_FALSE(c.armed());
    TEST_ASSERT_TRUE(send(c, 3, 0, 0, 281));
}
void test_invalid_range_and_header() {
    Core c; send(c, 1, 0, 0, 0); send(c, 2, 200, 200, 1);
    TEST_ASSERT_FALSE(send(c, 3, 1001, 0, 2));
    TEST_ASSERT_FALSE(c.armed());
    TEST_ASSERT_FALSE(send(c, 4, INT32_MIN, 0, 3));
    TEST_ASSERT_TRUE(send(c, 5, 0, 0, 4));
    uint8_t frame[18]; drive::encode({6, 100, 100}, frame); frame[2] = 2;
    auto crc = drive::crc16(frame, 16); frame[16] = crc; frame[17] = crc >> 8;
    for (auto byte : frame) c.receive(byte, 5);
    TEST_ASSERT_FALSE(c.armed());
}
void test_disconnect_retains_sequence() {
    Core c; send(c, 100, 0, 0, 0); send(c, 101, 300, 300, 1);
    c.disconnect();
    TEST_ASSERT_EQUAL_INT32(0, c.left());
    TEST_ASSERT_FALSE(send(c, 1, 0, 0, 10));
    TEST_ASSERT_TRUE(send(c, 102, 0, 0, 11));
}
void test_crc_known_vector() {
    const uint8_t data[] = "123456789";
    TEST_ASSERT_EQUAL_HEX16(0x29b1, drive::crc16(data, 9));
}
// Compiled from Python's independent struct/binascii encoder during verification.
void test_host_fixture() {
    const uint8_t frame[] = {
        0x44, 0x52, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xbe, 0x37
    };
    uint8_t encoded[18]; drive::encode({1, 0, 0}, encoded);
    TEST_ASSERT_EQUAL_MEMORY(frame, encoded, 18);
}
int main() {
    UNITY_BEGIN();
    RUN_TEST(test_startup_requires_zero);
    RUN_TEST(test_timeout_boundary_and_rearm);
    RUN_TEST(test_old_duplicate_and_ambiguous_do_not_refresh);
    RUN_TEST(test_sequence_and_clock_wrap);
    RUN_TEST(test_bad_crc_stops_and_resynchronises);
    RUN_TEST(test_split_frame_and_partial_expiry);
    RUN_TEST(test_invalid_range_and_header);
    RUN_TEST(test_disconnect_retains_sequence);
    RUN_TEST(test_crc_known_vector);
    RUN_TEST(test_host_fixture);
    return UNITY_END();
}

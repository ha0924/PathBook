-- 用户域初始化 SQL
-- 创建数据库
CREATE DATABASE IF NOT EXISTS pathbook DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pathbook;

-- 创建 users 表
CREATE TABLE users (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名，唯一',
    password_hash VARCHAR(255) NOT NULL        COMMENT 'bcrypt 哈希',
    is_active     BOOLEAN      DEFAULT TRUE    COMMENT '账号是否激活',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_username ON users(username);

-- 创建 user_profiles 表
CREATE TABLE user_profiles (
    id                       BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id                  BIGINT NOT NULL UNIQUE,
    home_cities              JSON COMMENT '常驻城市列表（数组，如 ["北京","天津"]），仅用于冷启动推荐，可空',
    home_locations           JSON COMMENT '常用出发地列表',
    budget_level             VARCHAR(20) DEFAULT '100-200' COMMENT '人均预算档位',
    transport_preferences    JSON COMMENT '交通偏好数组 ["taxi","metro","bus","walk"]',
    queue_tolerance_minutes  INT DEFAULT 15 COMMENT '排队容忍分钟数',
    walking_tolerance_meters INT DEFAULT 1000 COMMENT '步行容忍米数',
    food_preferences         JSON COMMENT '餐饮偏好数组',
    leisure_preferences      JSON COMMENT '休闲偏好数组',
    frequent_areas           JSON COMMENT '常去商圈数组',
    is_initialized           BOOLEAN DEFAULT FALSE COMMENT '是否完成首次配置',
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at               DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

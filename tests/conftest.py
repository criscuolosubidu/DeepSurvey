import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration", 
        action="store_true", 
        default=False, 
        help="运行集成测试"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: 标记集成测试")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    
    skip_integration = pytest.mark.skip(reason="需要使用 --run-integration 选项来运行集成测试")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration) 
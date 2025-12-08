"""修复.env配置文件"""
import os

env_file = '.env'
env_local_file = '.env.local'

print("🔧 检查环境配置文件...")

# 读取现有.env
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 当前 {env_file} 内容:")
    for line in lines:
        if 'DATABASE' in line:
            print(f"   {line.rstrip()}")
    
    # 注释掉DATABASE_URL和DEV_DATABASE_URL
    new_lines = []
    modified = False
    for line in lines:
        if line.strip().startswith('DATABASE_URL=') or line.strip().startswith('DEV_DATABASE_URL='):
            if not line.strip().startswith('#'):
                new_lines.append('# ' + line)
                modified = True
                print(f"✅ 已注释: {line.rstrip()}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"\n✅ {env_file} 已更新!")
    else:
        print(f"\n✅ {env_file} 无需修改")
else:
    print(f"⚠️  {env_file} 不存在")

# 检查.env.local
if os.path.exists(env_local_file):
    with open(env_local_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\n📄 当前 {env_local_file} 内容:")
    for line in lines:
        if 'DATABASE' in line:
            print(f"   {line.rstrip()}")
    
    # 注释掉DATABASE_URL和DEV_DATABASE_URL
    new_lines = []
    modified = False
    for line in lines:
        if line.strip().startswith('DATABASE_URL=') or line.strip().startswith('DEV_DATABASE_URL='):
            if not line.strip().startswith('#'):
                new_lines.append('# ' + line)
                modified = True
                print(f"✅ 已注释: {line.rstrip()}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified:
        with open(env_local_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"\n✅ {env_local_file} 已更新!")
    else:
        print(f"\n✅ {env_local_file} 无需修改")
else:
    print(f"\n⚠️  {env_local_file} 不存在")

print("\n" + "="*60)
print("✅ 配置修复完成!")
print("📌 现在将使用代码中的默认路径:")
print("   开发环境: backend/app-dev.db")
print("   生产环境: backend/app.db")
print("\n🔄 请重启Flask应用以使配置生效")
print("="*60)

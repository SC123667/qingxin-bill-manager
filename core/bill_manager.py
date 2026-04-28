#!/usr/bin/env python3
import sys
import os
import json
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
import base64

class BillManager:
    def __init__(self):
        # 获取程序所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)  # 返回到项目根目录
        
        # 尝试加载路径配置
        self._load_path_config(parent_dir)
        
        # 设置密码文件路径（总是在数据目录中）
        self.password_file = os.path.join(self.data_dir, "master_password.hash")
        self.current_account = "default"
        
        # 多人账单模式相关
        self.is_multi_person_mode = False  # 账单模式：False=单人模式，True=多人模式
        self.persons = ["默认"]  # 人员列表，单人模式下只有"默认"
        self.current_person = "默认"  # 当前选中的人员
        
        # 主账单关联管理
        self.master_person = None  # 主账单人员，None表示无主账单
        self.person_relations = {}  # 人员关系映射: {"关联人员": "主账单人员"}
        
        # 全局总预算（不分人员）
        self.total_budget = 0  # 全局总预算，所有人员共享
        
        # 默认分类（移除总预算，因为现在是全局设置）
        self.default_categories = [
            "五金", "住宿", "汽油", "饭钱", 
            "交通出行", "高速", "医疗", "赔钱", "电瓶", 
            "保险", "邮寄快递", "工资预支", "转账平账"
        ]
        # 动态分类列表（包含默认分类和自定义分类，不含总预算）
        self.categories = self.default_categories.copy()
        self.custom_categories = []  # 用户自定义分类
        
        # 账单数据结构：支持单人和多人模式
        # 单人模式：bills["默认"][category] = [bill1, bill2, ...]
        # 多人模式：bills[person][category] = [bill1, bill2, ...]
        self.bills = {"默认": {category: [] for category in self.categories}}
        
        # 为每个分类添加总账备注
        self.category_notes = {category: "" for category in self.categories}
        self.key = None
        self.accounts_list = []
        
        # 创建账本目录
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 确保备份目录存在
        if hasattr(self, 'backup_dir') and not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        # 注释掉数据迁移，让单人和多人模式完全独立
        # self._migrate_old_account_files()
    
    def _load_path_config(self, parent_dir):
        """加载路径配置"""
        config_file = os.path.join(parent_dir, "path_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.data_dir = config.get("data_path", os.path.join(parent_dir, "accounts_data"))
                self.backup_dir = config.get("backup_path", os.path.join(parent_dir, "password_backups"))
                
                # 确保路径存在
                os.makedirs(self.data_dir, exist_ok=True)
                os.makedirs(self.backup_dir, exist_ok=True)
                
            except Exception as e:
                # 配置文件损坏，使用默认路径
                self.data_dir = os.path.join(parent_dir, "accounts_data")
                self.backup_dir = os.path.join(parent_dir, "password_backups")
        else:
            # 没有配置文件，使用默认路径
            self.data_dir = os.path.join(parent_dir, "accounts_data")
            self.backup_dir = os.path.join(parent_dir, "password_backups")
    
    def get_data_directory(self):
        """获取数据存储目录"""
        return self.data_dir
    
    def get_backup_directory(self):
        """获取备份存储目录"""
        return getattr(self, 'backup_dir', os.path.join(os.path.dirname(self.data_dir), "password_backups"))
    
    def is_first_time_setup(self):
        """检查是否为首次设置"""
        return not os.path.exists(self.password_file)
        
    def _get_key_from_password(self, password):
        password_bytes = password.encode()
        key = base64.urlsafe_b64encode(hashlib.sha256(password_bytes).digest())
        return key
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _send_password_email(self, password):
        try:
            # 使用配置的备份目录
            backup_dir = self.get_backup_directory()
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_file = os.path.join(backup_dir, f"password_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            backup_content = f"""
=================================================
         账单管理系统密码备份文件
=================================================

主密码: {password}

重要提醒:
• 此密码一旦设置无法修改或找回
• 请将此文件保存到安全位置
• 建议多处备份以防丢失
• 删除此文件前请确保已记住密码

系统信息:
• 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 邮箱备份: 1844100669@qq.com
• 程序版本: v1.0

=================================================
         请妥善保管此密码备份
=================================================
"""
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            
            print(f"✅ 密码备份文件已创建: {backup_file}")
            
        except Exception as e:
            pass
    
    def _create_initial_default_account(self):
        """首次设置密码时创建默认账本（单人模式）"""
        self.current_account = "default"
        self.is_multi_person_mode = False
        self.persons = ["默认"]
        self.current_person = "默认"
        self.bills = {"默认": {category: [] for category in self.categories}}
        self.total_budget = 0
        self.category_notes = {category: "" for category in self.categories}
        self.save_data()
        print("首次使用，创建默认账本")
    
    def _ensure_account_exists(self):
        """确保当前模式至少有一个账本，如果没有则强制创建"""
        self.load_accounts_list()
        
        if not self.accounts_list:
            # 当前模式没有任何账本，强制创建一个
            self.current_account = "default"
            if self.is_multi_person_mode:
                self._initialize_multi_person_data()
            else:
                self._initialize_single_person_data()
            self.save_data()
            self.accounts_list = ["default"]
            print(f"强制创建{'多人' if self.is_multi_person_mode else '单人'}模式默认账本")
    
    def setup_password(self, password):
        if os.path.exists(self.password_file):
            return False
        
        with open(self.password_file, 'w') as f:
            f.write(self._hash_password(password))
        
        self.key = self._get_key_from_password(password)
        self._send_password_email(password)
        
        # 只有在首次设置密码时才创建默认账本
        self._create_initial_default_account()
        
        return True
    
    def verify_password(self, password):
        if not os.path.exists(self.password_file):
            return False
        
        with open(self.password_file, 'r') as f:
            stored_hash = f.read()
        
        if self._hash_password(password) == stored_hash:
            self.key = self._get_key_from_password(password)
            return True
        return False
    
    def get_account_file_path(self, account_name):
        """获取指定账本的加密文件路径"""
        # 根据当前模式选择不同的文件前缀
        if self.is_multi_person_mode:
            return os.path.join(self.data_dir, f"multi_{account_name}.encrypted")
        else:
            return os.path.join(self.data_dir, f"single_{account_name}.encrypted")
    
    def load_accounts_list(self):
        """加载当前模式的账本列表"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.accounts_list = []
        prefix = "multi_" if self.is_multi_person_mode else "single_"
        
        for file in os.listdir(self.data_dir):
            if file.endswith('.encrypted') and file.startswith(prefix):
                # 移除前缀和.encrypted后缀
                account_name = file[len(prefix):-10]
                self.accounts_list.append(account_name)
        
        # 不再自动添加默认账本到列表中，让列表真实反映文件系统状态
        return self.accounts_list
    
    def load_data(self, account_name=None):
        if account_name:
            self.current_account = account_name
            
        # 如果current_account为None，不进行任何操作
        if self.current_account is None:
            return
            
        account_file = self.get_account_file_path(self.current_account)
        
        if not os.path.exists(account_file) or not self.key:
            # 文件不存在时不自动创建，只初始化内存数据为空状态
            self.bills = {"默认": {category: [] for category in self.categories}}
            self.total_budget = 0
            self.category_notes = {category: "" for category in self.categories}
            self.persons = ["默认"]
            self.current_person = "默认"
            return
        
        try:
            with open(account_file, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = Fernet(self.key)
            decrypted_data = fernet.decrypt(encrypted_data)
            loaded_data = json.loads(decrypted_data.decode())
            
            # 兼容旧格式数据和新格式数据
            if isinstance(loaded_data, dict) and "bills" in loaded_data:
                old_bills = loaded_data["bills"]
                self.category_notes = loaded_data.get("category_notes", {category: "" for category in self.categories if category != "总预算"})
                # 加载自定义分类
                self.custom_categories = loaded_data.get("custom_categories", [])
                # 加载多人模式相关数据
                self.is_multi_person_mode = loaded_data.get("is_multi_person_mode", False)
                self.persons = loaded_data.get("persons", ["默认"])
                self.current_person = loaded_data.get("current_person", "默认")
                
                # 加载主账单关联数据
                self.master_person = loaded_data.get("master_person", None)
                self.person_relations = loaded_data.get("person_relations", {})
                
                # 加载全局预算（新格式）或从旧格式迁移
                if "total_budget" in loaded_data:
                    # 新格式：已有全局预算
                    self.total_budget = loaded_data["total_budget"]
                else:
                    # 旧格式：从个人预算中迁移到全局预算
                    self.total_budget = 0
                    # 尝试从第一个人员的总预算中获取
                    if isinstance(old_bills, dict):
                        for person_name, person_data in old_bills.items():
                            if isinstance(person_data, dict) and "总预算" in person_data:
                                if person_data["总预算"] and len(person_data["总预算"]) > 0:
                                    self.total_budget = max(self.total_budget, sum(person_data["总预算"]))
                                    break
                
                # 更新完整分类列表
                self.categories = self.default_categories.copy() + self.custom_categories
                
                # 判断并转换数据格式
                if isinstance(old_bills, dict) and "默认" in old_bills:
                    # 新格式：已经是多人模式的数据结构
                    self.bills = old_bills
                else:
                    # 旧格式：单人模式数据结构，需要转换
                    self.bills = {"默认": old_bills}
                    self.is_multi_person_mode = False
                    self.persons = ["默认"]
                    self.current_person = "默认"
                
                # 确保所有人员和分类都有对应的数据（不包括总预算）
                for person in self.persons:
                    if person not in self.bills:
                        self.bills[person] = {category: [] for category in self.categories}
                    else:
                        for category in self.categories:
                            if category not in self.bills[person]:
                                self.bills[person][category] = []
                        # 移除旧的总预算数据
                        if "总预算" in self.bills[person]:
                            del self.bills[person]["总预算"]
                
                # 确保所有分类都有备注
                for category in self.categories:
                    if category != "总预算" and category not in self.category_notes:
                        self.category_notes[category] = ""
            else:
                # 最旧格式，只有bills数据
                self.bills = {"默认": loaded_data}
                self.custom_categories = []
                self.category_notes = {category: "" for category in self.categories if category != "总预算"}
                self.is_multi_person_mode = False
                self.persons = ["默认"]
                self.current_person = "默认"
                self.total_budget = 0
                self.master_person = None
                self.person_relations = {}
                
        except Exception as e:
            # 如果解密失败，初始化空数据
            self.bills = {"默认": {category: [] for category in self.categories}}
            self.total_budget = 0
            self.category_notes = {category: "" for category in self.categories if category != "总预算"}
            self.is_multi_person_mode = False
            self.persons = ["默认"]
            self.current_person = "默认"
            self.master_person = None
            self.person_relations = {}
    
    def save_data(self):
        if not self.key or self.current_account is None:
            return
        
        account_file = self.get_account_file_path(self.current_account)
        
        try:
            fernet = Fernet(self.key)
            # 保存账单数据、分类备注、自定义分类、多人模式数据和全局预算
            data_to_save = {
                "bills": self.bills,
                "category_notes": self.category_notes,
                "custom_categories": self.custom_categories,
                "is_multi_person_mode": self.is_multi_person_mode,
                "persons": self.persons,
                "current_person": self.current_person,
                "total_budget": self.total_budget,
                "master_person": self.master_person,
                "person_relations": self.person_relations
            }
            data_str = json.dumps(data_to_save, ensure_ascii=False, indent=2)
            encrypted_data = fernet.encrypt(data_str.encode())
            
            with open(account_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            pass
    
    def create_new_account(self, account_name):
        """创建新账本"""
        if account_name in self.accounts_list:
            return False  # 账本已存在
        
        # 为新账本初始化数据
        old_bills = self.bills.copy()
        old_notes = self.category_notes.copy()
        old_custom_categories = self.custom_categories.copy()
        old_mode = self.is_multi_person_mode
        old_persons = self.persons.copy()
        old_person = self.current_person
        old_account = self.current_account
        
        self.current_account = account_name
        # 新账本使用默认分类，但保持当前模式设置
        self.custom_categories = []
        self.categories = self.default_categories.copy()
        self.bills = {"默认": {category: [] for category in self.categories}}
        self.total_budget = 0
        self.category_notes = {category: "" for category in self.categories if category != "总预算"}
        # 保持原来的多人模式设置，不强制改为单人模式
        # self.is_multi_person_mode = False  # 移除这行
        self.persons = ["默认"]
        self.current_person = "默认"
        
        # 保存新账本
        self.save_data()
        
        # 恢复原来的数据
        self.bills = old_bills
        self.category_notes = old_notes
        self.custom_categories = old_custom_categories
        self.categories = self.default_categories.copy() + self.custom_categories
        self.is_multi_person_mode = old_mode
        self.persons = old_persons
        self.current_person = old_person
        self.current_account = old_account
        
        # 更新账本列表
        self.accounts_list.append(account_name)
        
        return True
    
    def switch_account(self, account_name):
        """切换账本"""
        if account_name not in self.accounts_list:
            return False
        
        # 保存当前账本数据
        self.save_data()
        
        # 切换到新账本
        self.load_data(account_name)
        
        return True
    
    def delete_account(self, account_name):
        """删除账本（必须保证至少有一个账本）"""
        if account_name not in self.accounts_list:
            return False, "账本不存在"
        
        # 强制确保至少有一个账本
        if len(self.accounts_list) <= 1:
            return False, "每个模式至少需要保留一个账本"
        
        account_file = self.get_account_file_path(account_name)
        
        try:
            # 如果删除的是当前账本，先切换到其他账本，避免保存被删除的账本
            if self.current_account == account_name:
                # 找到一个不是要删除的账本
                next_account = None
                for acc in self.accounts_list:
                    if acc != account_name:
                        next_account = acc
                        break
                
                if next_account:
                    # 直接切换，不保存当前（即将删除的）账本数据
                    self.current_account = next_account
                    self.load_data(next_account)
            
            # 删除文件
            if os.path.exists(account_file):
                os.remove(account_file)
            
            # 从账本列表中移除
            self.accounts_list.remove(account_name)
                
            return True, "账本删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def rename_account(self, old_name, new_name):
        """重命名账本"""
        if old_name not in self.accounts_list:
            return False, "原账本不存在"
        
        if not new_name or not new_name.strip():
            return False, "新账本名称不能为空"
        
        new_name = new_name.strip()
        
        # 检查新名称是否已存在
        if new_name in self.accounts_list:
            return False, "账本名称已存在"
        
        # 检查新名称是否包含非法字符
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in new_name for char in invalid_chars):
            return False, "账本名称包含非法字符"
        
        old_file = self.get_account_file_path(old_name)
        new_file = self.get_account_file_path(new_name)
        
        try:
            # 重命名文件
            if os.path.exists(old_file):
                os.rename(old_file, new_file)
            
            # 更新账本列表
            index = self.accounts_list.index(old_name)
            self.accounts_list[index] = new_name
            
            # 如果重命名的是当前账本，更新当前账本名称
            if self.current_account == old_name:
                self.current_account = new_name
                
            return True, "账本重命名成功"
        except Exception as e:
            return False, f"重命名失败: {str(e)}"
    
    def get_current_account(self):
        """获取当前账本名称"""
        return self.current_account
    
    def add_bill(self, category, amount, description="", person=None):
        if category in self.categories:
            # 如果没有指定人员，使用当前选中的人员
            target_person = person if person else self.current_person
            
            bill_entry = {
                "amount": float(amount),
                "description": description,
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 确保目标人员存在
            if target_person not in self.bills:
                self.bills[target_person] = {cat: [] for cat in self.categories}
            
            self.bills[target_person][category].append(bill_entry)
            self.save_data()
            return True
        return False
    
    def delete_bill(self, category, bill_index, person=None):
        """删除指定分类中的指定账单"""
        target_person = person if person else self.current_person
        
        if (category in self.categories and 
            target_person in self.bills and 
            category in self.bills[target_person]):
            bills = self.bills[target_person][category]
            if 0 <= bill_index < len(bills):
                deleted_bill = bills.pop(bill_index)
                self.save_data()
                return deleted_bill
        return None
    
    def delete_bills_batch(self, bill_list, person=None):
        """批量删除账单
        bill_list: [(category, index), (category, index), ...]
        注意：索引必须从大到小排序以避免删除后索引变化的问题
        """
        deleted_bills = []
        target_person = person if person else self.current_person
        # 按索引从大到小排序，避免删除后索引变化
        bill_list.sort(key=lambda x: x[1], reverse=True)
        
        for category, bill_index in bill_list:
            if (category in self.categories and
                target_person in self.bills and
                category in self.bills[target_person]):
                bills = self.bills[target_person][category]
                if 0 <= bill_index < len(bills):
                    deleted_bills.append((category, bills.pop(bill_index)))
        
        if deleted_bills:
            self.save_data()
        
        return deleted_bills
    
    def set_category_note(self, category, note):
        """设置分类备注"""
        if category in self.categories and category != "总预算":
            self.category_notes[category] = note.strip()
            self.save_data()
            return True
        return False
    
    def get_category_note(self, category):
        """获取分类备注"""
        return self.category_notes.get(category, "")
    
    def get_category_total(self, category, person=None):
        """获取指定分类的总金额，支持单人/多人模式"""
        if category == "总预算":
            # 返回全局预算
            return self.total_budget
        
        if person:
            # 获取指定人员的分类总额
            if person in self.bills and category in self.bills[person]:
                return sum(bill["amount"] for bill in self.bills[person][category])
            return 0
        else:
            # 获取当前选中人员或所有人员的总额
            if self.is_multi_person_mode:
                # 多人模式：返回当前选中人员的总额
                if self.current_person in self.bills and category in self.bills[self.current_person]:
                    return sum(bill["amount"] for bill in self.bills[self.current_person][category])
                return 0
            else:
                # 单人模式：返回默认人员的总额
                if "默认" in self.bills and category in self.bills["默认"]:
                    return sum(bill["amount"] for bill in self.bills["默认"][category])
                return 0
    
    def get_all_persons_category_total(self, category):
        """获取所有人员在指定分类的总金额"""
        if category == "总预算":
            # 返回全局预算
            return self.total_budget
        
        total = 0
        for person in self.persons:
            if person in self.bills and category in self.bills[person]:
                total += sum(bill["amount"] for bill in self.bills[person][category])
        return total
    
    def search_bills(self, keyword, person=None):
        """搜索账单，支持指定人员搜索"""
        results = []
        keyword_lower = keyword.lower()
        
        if person:
            # 搜索指定人员的账单
            search_persons = [person] if person in self.bills else []
        else:
            # 搜索当前选中人员的账单
            if self.is_multi_person_mode:
                search_persons = [self.current_person] if self.current_person in self.bills else []
            else:
                search_persons = ["默认"] if "默认" in self.bills else []
        
        for person_name in search_persons:
            person_bills = self.bills[person_name]
            for category, bills in person_bills.items():
                if category == "总预算":
                    continue
                for bill in bills:
                    if (keyword_lower in bill.get("description", "").lower() or 
                        keyword_lower in category.lower() or
                        keyword in str(bill["amount"])):
                        result = {
                            "category": category,
                            "amount": bill["amount"],
                            "description": bill.get("description", ""),
                            "date": bill["date"]
                        }
                        # 在多人模式下添加人员信息
                        if self.is_multi_person_mode:
                            result["person"] = person_name
                        results.append(result)
        return results
    
    def search_all_persons_bills(self, keyword):
        """搜索所有人员的账单"""
        results = []
        for person_name in self.persons:
            if person_name in self.bills:
                person_results = self.search_bills(keyword, person_name)
                results.extend(person_results)
        return results
    
    def add_custom_category(self, category_name):
        """添加自定义分类"""
        category_name = category_name.strip()
        if not category_name:
            return False, "分类名称不能为空"
        
        if category_name in self.categories:
            return False, "分类已存在"
        
        if category_name == "总预算":
            return False, "不能使用保留分类名"
        
        # 添加到自定义分类列表
        self.custom_categories.append(category_name)
        # 更新完整分类列表
        self.categories = self.default_categories.copy() + self.custom_categories
        # 为所有人员初始化分类数据
        for person in self.persons:
            if person in self.bills:
                self.bills[person][category_name] = []
        self.category_notes[category_name] = ""
        # 保存数据
        self.save_data()
        return True, "分类添加成功"
    
    def remove_custom_category(self, category_name):
        """删除自定义分类"""
        if category_name not in self.custom_categories:
            return False, "只能删除自定义分类"
        
        for person_data in self.bills.values():
            if isinstance(person_data, dict) and person_data.get(category_name):
                return False, "该分类下还有账单记录，无法删除"
        
        # 从自定义分类中移除
        self.custom_categories.remove(category_name)
        # 更新完整分类列表
        self.categories = self.default_categories.copy() + self.custom_categories
        # 删除所有人员下的该分类空列表
        for person_data in self.bills.values():
            if isinstance(person_data, dict) and category_name in person_data:
                del person_data[category_name]
        if category_name in self.category_notes:
            del self.category_notes[category_name]
        # 保存数据
        self.save_data()
        return True, "分类删除成功"
    
    def get_custom_categories(self):
        """获取自定义分类列表"""
        return self.custom_categories.copy()
    
    def is_custom_category(self, category_name):
        """检查是否为自定义分类"""
        return category_name in self.custom_categories
    
    # ============= 多人模式管理方法 =============
    
    def switch_to_multi_person_mode(self):
        """切换到多人模式"""
        if not self.is_multi_person_mode:
            self.is_multi_person_mode = True
            
            # 重新加载多人模式的账本列表
            self.load_accounts_list()
            
            # 检查整个系统是否有任何账本文件（包括单人和多人模式）
            all_account_files = []
            if os.path.exists(self.data_dir):
                all_account_files = [f for f in os.listdir(self.data_dir) if f.endswith('.encrypted')]
            
            # 检查多人模式是否有账本
            if self.accounts_list:
                # 如果多人模式有账本，优先选择current_account，如果不存在则选择最后一个
                if self.current_account in self.accounts_list:
                    self.load_data(self.current_account)
                else:
                    # 选择最后一个账本（通常是最新创建的）
                    self.current_account = self.accounts_list[-1]
                    self.load_data(self.current_account)
            else:
                # 如果多人模式没有账本，强制创建一个
                self._ensure_account_exists()
                if self.current_account:
                    self.load_data(self.current_account)
                
            return True
        return False
    
    def switch_to_single_person_mode(self):
        """切换到单人模式"""
        if self.is_multi_person_mode:
            self.is_multi_person_mode = False
            self.current_person = "默认"
            
            # 重新加载单人模式的账本列表
            self.load_accounts_list()
            
            # 检查整个系统是否有任何账本文件（包括单人和多人模式）
            all_account_files = []
            if os.path.exists(self.data_dir):
                all_account_files = [f for f in os.listdir(self.data_dir) if f.endswith('.encrypted')]
            
            # 检查单人模式是否有账本
            if self.accounts_list:
                # 如果单人模式有账本，优先选择current_account，如果不存在则选择最后一个
                if self.current_account in self.accounts_list:
                    self.load_data(self.current_account)
                else:
                    # 选择最后一个账本（通常是最新创建的）
                    self.current_account = self.accounts_list[-1]
                    self.load_data(self.current_account)
            else:
                # 如果单人模式没有账本，强制创建一个
                self._ensure_account_exists()
                if self.current_account:
                    self.load_data(self.current_account)
                
            return True
        return False
    
    def _initialize_multi_person_data(self):
        """初始化多人模式数据结构"""
        self.persons = ["默认"]
        self.current_person = "默认"
        # 重置账单数据结构
        self.bills = {"默认": {category: [] for category in self.categories}}
        # 重置分类备注
        self.category_notes = {category: "" for category in self.categories}
        self.total_budget = 0
    
    def _initialize_single_person_data(self):
        """初始化单人模式数据结构"""
        self.persons = ["默认"]
        self.current_person = "默认"
        # 重置账单数据结构
        self.bills = {"默认": {category: [] for category in self.categories}}
        # 重置分类备注
        self.category_notes = {category: "" for category in self.categories}
        self.total_budget = 0
    
    def _create_default_multi_person_account(self):
        """创建多人模式默认账本"""
        self._initialize_multi_person_data()
        self.save_data()
        print("创建多人模式默认账本")
    
    def _create_default_single_person_account(self):
        """创建单人模式默认账本"""
        self._initialize_single_person_data()
        self.save_data()
        print("创建单人模式默认账本")
    
    def add_person(self, person_name):
        """添加新人员"""
        person_name = person_name.strip()
        if not person_name:
            return False, "人员名称不能为空"
        
        if person_name in self.persons:
            return False, "人员已存在"
        
        # 添加人员到列表
        self.persons.append(person_name)
        # 为新人员初始化账单数据（不包括总预算）
        self.bills[person_name] = {category: [] for category in self.categories}
        
        self.save_data()
        return True, "人员添加成功"
    
    def remove_person(self, person_name):
        """删除人员"""
        if person_name == "默认":
            return False, "不能删除默认人员"
        
        if person_name not in self.persons:
            return False, "人员不存在"
        
        # 检查是否有账单记录
        if person_name in self.bills:
            has_bills = False
            for category, bills in self.bills[person_name].items():
                if bills:  # 只要有任何账单记录就不能删除
                    has_bills = True
                    break
            
            if has_bills:
                return False, "该人员下还有账单记录，无法删除"
        
        # 删除人员
        self.persons.remove(person_name)
        if person_name in self.bills:
            del self.bills[person_name]
        
        # 如果删除的是当前选中人员，切换到默认人员
        if self.current_person == person_name:
            self.current_person = "默认"
        
        self.save_data()
        return True, "人员删除成功"
    
    def switch_current_person(self, person_name):
        """切换当前人员"""
        if person_name in self.persons:
            self.current_person = person_name
            self.save_data()
            return True
        return False
    
    def get_persons_list(self):
        """获取人员列表"""
        return self.persons.copy()
    
    def get_current_person(self):
        """获取当前选中的人员"""
        return self.current_person
    
    def is_multi_person_mode_enabled(self):
        """检查是否为多人模式"""
        return self.is_multi_person_mode
    
    # ============= 全局预算管理方法 =============
    
    def set_total_budget(self, budget_amount):
        """设置全局总预算"""
        try:
            self.total_budget = float(budget_amount)
            self.save_data()
            return True
        except (ValueError, TypeError):
            return False
    
    def get_total_budget(self):
        """获取全局总预算"""
        return self.total_budget
    
    def get_total_spent(self):
        """获取所有人员的总支出"""
        total_spent = 0
        for person in self.persons:
            if person in self.bills:
                for category in self.categories:
                    if category != "总预算" and category in self.bills[person]:
                        total_spent += sum(bill["amount"] for bill in self.bills[person][category])
        return total_spent
    
    def get_remaining_budget(self):
        """获取剩余预算"""
        return self.total_budget - self.get_total_spent()
    
    # ============= 主账单管理功能 =============
    
    def set_master_person(self, person_name):
        """设置主账单人员"""
        if person_name not in self.persons:
            return False, "人员不存在"
        
        if person_name == self.master_person:
            return False, "该人员已经是主账单"
        
        self.master_person = person_name
        # 清理旧的关联关系
        self.person_relations = {}
        self.save_data()
        return True, f"已设置 {person_name} 为主账单"
    
    def get_master_person(self):
        """获取主账单人员"""
        return self.master_person
    
    def set_person_relation(self, child_person, master_person):
        """设置人员关联关系"""
        if child_person not in self.persons or master_person not in self.persons:
            return False, "人员不存在"
        
        if child_person == master_person:
            return False, "不能关联自己"
        
        self.person_relations[child_person] = master_person
        self.save_data()
        return True, f"已将 {child_person} 关联到 {master_person}"
    
    def remove_person_relation(self, person_name):
        """移除人员关联关系"""
        if person_name in self.person_relations:
            del self.person_relations[person_name]
            self.save_data()
            return True, f"已移除 {person_name} 的关联关系"
        return False, "该人员没有关联关系"
    
    def get_person_relations(self):
        """获取所有人员关联关系"""
        return self.person_relations.copy()
    
    def is_master_person(self, person_name):
        """检查是否为主账单人员"""
        return person_name == self.master_person
    
    def get_related_master(self, person_name):
        """获取关联的主账单人员"""
        return self.person_relations.get(person_name, None)
    
    def add_transfer_bill(self, from_person, to_person, amount, description="转账平账"):
        """添加转账平账记录"""
        if from_person not in self.persons or to_person not in self.persons:
            return False, "人员不存在"
        
        if amount <= 0:
            return False, "转账金额必须大于0"
        
        # 在转账方添加支出记录（转账平账分类）
        if self.add_bill("转账平账", amount, f"向 {to_person} 转账: {description}", from_person):
            # 在接收方添加收入记录（负金额表示收入）
            if self.add_bill("转账平账", -amount, f"来自 {from_person} 转账: {description}", to_person):
                return True, f"转账成功：{from_person} → {to_person} ¥{amount:.2f}"
            else:
                # 如果接收方记录失败，回滚转账方记录
                # 这里需要更复杂的回滚逻辑，简化处理
                return False, "转账失败，请重试"
        
        return False, "转账失败"
    
    def get_person_balance(self, person_name):
        """获取指定人员的账单余额（支出-收入）"""
        if person_name not in self.persons:
            return 0
        
        total_expense = 0
        total_income = 0
        
        if person_name in self.bills:
            for category, bills in self.bills[person_name].items():
                if category != "总预算":
                    for bill in bills:
                        amount = bill["amount"]
                        if amount > 0:
                            total_expense += amount
                        else:
                            total_income += abs(amount)  # 负金额转为正数
        
        return total_expense - total_income
    
    def get_transfer_summary(self):
        """获取转账平账汇总信息"""
        transfer_summary = {}
        
        for person in self.persons:
            if person in self.bills and "转账平账" in self.bills[person]:
                transfer_bills = self.bills[person]["转账平账"]
                person_transfers = []
                
                for bill in transfer_bills:
                    person_transfers.append({
                        "amount": bill["amount"],
                        "description": bill.get("description", ""),
                        "date": bill["date"]
                    })
                
                if person_transfers:
                    transfer_summary[person] = person_transfers
        
        return transfer_summary
    
    def quick_balance_account(self, target_person):
        """快速平账：将目标人员的支出转移到主账单"""
        if not self.master_person:
            return False, "请先设置主账单人员"
        
        if target_person not in self.persons:
            return False, "目标人员不存在"
        
        if target_person == self.master_person:
            return False, "不能向自己转账"
        
        # 计算目标人员的实际支出（不包括转账记录）
        actual_expense = 0
        if target_person in self.bills:
            for category, bills in self.bills[target_person].items():
                if category != "总预算" and category != "转账平账":
                    actual_expense += sum(bill["amount"] for bill in bills)
        
        if actual_expense <= 0:
            return False, f"{target_person} 没有需要平账的支出"
        
        # 执行转账
        return self.add_transfer_bill(
            self.master_person, 
            target_person, 
            actual_expense, 
            f"平账 {target_person} 的所有支出"
        )

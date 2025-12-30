from typing import Dict, Any, Tuple

class Evaluator:
    """
    Evaluator Logic - Updated for Advanced Schema
    """
    
    @staticmethod
    def validate(data) -> Tuple[bool, Dict[str, Any]]:
        report = {
            "checks": [],
            "status": "FAIL"
        }
        
        if not data:
            return False, {"error": "No data input"}

        # 1. Check Mandatory Fields
        # Kiểm tra xem có tên cửa hàng không (và không phải là Unknown)
        has_merchant = bool(data.merchant_name and data.merchant_name != "Unknown")
        has_total = data.total_amount > 0
        
        report["checks"].append({"rule": "Has Merchant Name", "passed": has_merchant})
        report["checks"].append({"rule": "Has Positive Total", "passed": has_total})

        # 2. Math Consistency Check (Logic toán học)
        if data.items:
            # SỬA LỖI Ở ĐÂY: Dùng item.total_price thay vì item.price
            items_sum = sum(item.total_price for item in data.items)
            
            if data.total_amount > 0:
                # Cho phép sai số 15% (do thuế/phí chưa tách được hết)
                diff = abs(items_sum - data.total_amount)
                is_math_consistent = diff <= (data.total_amount * 0.15)
            else:
                is_math_consistent = False
                
            report["checks"].append({
                "rule": "Math Consistency (Items Sum ≈ Total)", 
                "passed": is_math_consistent,
                "info": f"Items Sum: {items_sum:,.0f} | Total: {data.total_amount:,.0f}"
            })
        else:
            report["checks"].append({"rule": "Items Detected", "passed": False})

        # Final Decision
        passed_count = sum(1 for c in report["checks"] if c["passed"])
        # Pass nếu đúng ít nhất 2 tiêu chí quan trọng
        is_success = passed_count >= 2
        report["status"] = "PASS" if is_success else "FAIL"
        
        return is_success, report
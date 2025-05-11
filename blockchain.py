import hashlib
import time
import json
from utils import hash_data
from difflib import SequenceMatcher

class Blockchain:
    def __init__(self):
        self.chain = []
        self.reports = {}
        self.user_submission_count = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'report_id': 'genesis',
            'data': 'Genesis Block',
            'previous_hash': '0',
            'hash': self.calculate_hash(0, 'genesis', 'Genesis Block', '0'),
            'creation_time': 0
        }
        self.chain.append(genesis_block)

    def calculate_hash(self, index, report_id, data, previous_hash):
        block_string = f'{index}{report_id}{data}{previous_hash}'
        return hashlib.sha256(block_string.encode()).hexdigest()

    def validate_report(self, data, author, is_update=False, previous_data=None):
        if len(data.strip()) < 10:
            return 'Report too short (minimum 10 characters)'
        if len(data) > 500:
            return 'Report too long (maximum 500 characters)'
        if not any(c.isalpha() for c in data):
            return 'Report must contain at least one letter'
        forbidden_keywords = ['malicious', 'hack', 'exploit']
        if any(keyword in data.lower() for keyword in forbidden_keywords):
            return 'Report contains forbidden keywords'
        if not is_update:
            self.user_submission_count[author] = self.user_submission_count.get(author, 0) + 1
            if self.user_submission_count[author] > 5:
                return 'Submission limit exceeded (max 5 reports per user)'
        if is_update and previous_data:
            similarity = SequenceMatcher(None, data, previous_data).ratio()
            if similarity > 0.9:
                return 'Updated report must differ by at least 10%'
        return 'valid'

    def add_block(self, report_id, data, author):
        previous_block = self.chain[-1]
        index = len(self.chain)
        start_time = time.time()
        block = {
            'index': index,
            'timestamp': start_time,
            'report_id': report_id,
            'data': data,
            'author': author,
            'previous_hash': previous_block['hash'],
            'hash': self.calculate_hash(index, report_id, data, previous_block['hash']),
            'creation_time': time.time() - start_time
        }
        self.chain.append(block)
        self.reports[report_id] = data
        return block

    def update_report(self, report_id, new_data, author):
        if report_id in self.reports:
            validation_result = self.validate_report(new_data, author, is_update=True, previous_data=self.reports[report_id])
            if validation_result == 'valid':
                self.reports[report_id] = new_data
                self.add_block(report_id, new_data, author)
                return 'valid'
            return validation_result
        return 'Report not found'

    def get_reports(self):
        return self.reports

    def get_student_records(self):
        return self.chain

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current['hash'] != self.calculate_hash(current['index'], current['report_id'], current['data'], current['previous_hash']):
                return False
            if current['previous_hash'] != previous['hash']:
                return False
        return True

    def simulate_attack(self, attack_type):
        if len(self.chain) <= 1:
            return {'result': 'Not enough blocks to simulate attack', 'details': {}}
        if attack_type == 'tampering':
            original_data = self.chain[1]['data']
            original_hash = self.chain[1]['hash']
            self.chain[1]['data'] = 'Tampered Data'
            self.chain[1]['hash'] = self.calculate_hash(
                self.chain[1]['index'], self.chain[1]['report_id'], self.chain[1]['data'], self.chain[1]['previous_hash'])
            is_detected = not self.validate_chain()
            result = 'Tampering attempt detected' if is_detected else 'Tampering undetected'
            details = {
                'block_index': 1,
                'original_data': original_data,
                'tampered_data': 'Tampered Data',
                'original_hash': original_hash,
                'new_hash': self.chain[1]['hash'],
                'description': 'Modified data in block 1 and recalculated hash to test chain integrity.'
            }
            self.chain[1]['data'] = original_data
            self.chain[1]['hash'] = original_hash
            return {'result': result, 'details': details}
        elif attack_type == 'hash_collision':
            original_data = self.chain[1]['data']
            original_hash = self.chain[1]['hash']
            for i in range(1000):
                test_data = f'TestData{i}'
                test_hash = self.calculate_hash(self.chain[1]['index'], self.chain[1]['report_id'], test_data, self.chain[1]['previous_hash'])
                if test_hash == original_hash:
                    return {
                        'result': 'Hash collision detected',
                        'details': {
                            'block_index': 1,
                            'original_data': original_data,
                            'colliding_data': test_data,
                            'hash': original_hash,
                            'description': 'Found different data producing the same hash as block 1.'
                        }
                    }
            return {
                'result': 'No hash collision found',
                'details': {
                    'block_index': 1,
                    'original_data': original_data,
                    'attempted_data': 'TestData0 to TestData999',
                    'hash': original_hash,
                    'description': 'Tried 1000 different data inputs to find a matching hash; none found.'
                }
            }
        elif attack_type == 'double_spending':
            if len(self.chain) > 2:
                original_length = len(self.chain)
                duplicated_block = self.chain[1].copy()
                self.chain.append(duplicated_block)
                is_detected = not self.validate_chain()
                result = 'Double-spending attempt detected' if is_detected else 'Double-spending undetected'
                details = {
                    'block_index': 1,
                    'duplicated_block_index': original_length,
                    'data': duplicated_block['data'],
                    'hash': duplicated_block['hash'],
                    'description': 'Duplicated block 1 to simulate using the same report twice.'
                }
                self.chain.pop()
                return {'result': result, 'details': details}
            return {'result': 'Not enough blocks for double-spending simulation', 'details': {}}
        return {'result': 'Invalid attack type', 'details': {}}

    def get_quality_metrics(self):
        metrics = {
            'chain_length': len(self.chain),
            'average_block_time': sum(block['creation_time'] for block in self.chain) / len(self.chain) if self.chain else 0,
            'validation_status': self.validate_chain(),
            'report_compliance': sum(1 for report in self.reports.values() if self.validate_report(report, 'system', is_update=True) == 'valid') / len(self.reports) if self.reports else 1.0
        }
        quality_score = (metrics['validation_status'] * 0.4 + metrics['report_compliance'] * 0.4 + (1 - metrics['average_block_time'] / 0.1 if metrics['average_block_time'] > 0 else 1) * 0.2) * 100
        metrics['quality_score'] = round(quality_score, 2)
        return metrics
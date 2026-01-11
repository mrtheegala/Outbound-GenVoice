"""
Prior Authorization Storage Manager
Handles saving, loading, and querying prior authorization records
"""

import os
import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from healthcare_rcm.models.prior_auth_models import (
    PriorAuthRecord, AuthorizationStatus, CallOutcome
)

logger = logging.getLogger(__name__)


class PriorAuthStorage:
    """Manages storage and retrieval of prior authorization records"""
    
    def __init__(self, storage_dir: str = "prior_auth_records"):
        """
        Initialize storage manager
        
        Args:
            storage_dir: Directory to store prior auth records
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        (self.storage_dir / "approved").mkdir(exist_ok=True)
        (self.storage_dir / "pending").mkdir(exist_ok=True)
        (self.storage_dir / "denied").mkdir(exist_ok=True)
        (self.storage_dir / "failed").mkdir(exist_ok=True)
        
        logger.info(f"Initialized prior auth storage at: {self.storage_dir.absolute()}")
    
    def save_record(self, record: PriorAuthRecord, overwrite: bool = True) -> str:
        """
        Save prior authorization record to file
        
        Args:
            record: PriorAuthRecord to save
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to saved file
        """
        # Determine subdirectory based on status
        subdir = self._get_subdir_for_status(record.authorization.status)
        
        # Create filename: YYYYMMDD_HHMMSS_CallID.json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{record.call_id}.json"
        filepath = self.storage_dir / subdir / filename
        
        # Check if file exists
        if filepath.exists() and not overwrite:
            logger.warning(f"File already exists: {filepath}")
            return str(filepath)
        
        # Save record
        try:
            record.updated_at = datetime.now()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(record.to_json())
            
            logger.info(f"Saved prior auth record to: {filepath}")
            
            # Also save a summary file
            self._save_summary(record, filepath)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving prior auth record: {e}")
            raise
    
    def _save_summary(self, record: PriorAuthRecord, json_filepath: Path):
        """Save a human-readable summary alongside JSON"""
        summary_filepath = json_filepath.with_suffix('.txt')
        
        try:
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"PRIOR AUTHORIZATION CALL SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Call ID: {record.call_id}\n")
                f.write(f"Date: {record.call_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Insurance: {record.insurance_company}\n")
                f.write(f"Status: {record.authorization.status.value.upper()}\n")
                f.write(f"Outcome: {record.call_outcome.value.upper()}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("PATIENT INFORMATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Name: {record.patient.name}\n")
                if record.patient.date_of_birth:
                    f.write(f"DOB: {record.patient.date_of_birth}\n")
                if record.patient.member_id:
                    f.write(f"Member ID: {record.patient.member_id}\n")
                f.write("\n")
                
                f.write("-" * 80 + "\n")
                f.write("PROVIDER INFORMATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Name: {record.provider.name}\n")
                if record.provider.npi:
                    f.write(f"NPI: {record.provider.npi}\n")
                f.write("\n")
                
                f.write("-" * 80 + "\n")
                f.write("PROCEDURE\n")
                f.write("-" * 80 + "\n")
                f.write(f"CPT Code: {record.procedure.cpt_code}\n")
                if record.procedure.description:
                    f.write(f"Description: {record.procedure.description}\n")
                if record.procedure.icd_code:
                    f.write(f"Diagnosis: {record.procedure.icd_code}\n")
                f.write("\n")
                
                f.write("-" * 80 + "\n")
                f.write("AUTHORIZATION DETAILS\n")
                f.write("-" * 80 + "\n")
                if record.authorization.authorization_number:
                    f.write(f"✅ Authorization Number: {record.authorization.authorization_number}\n")
                if record.authorization.reference_number:
                    f.write(f"Reference Number: {record.authorization.reference_number}\n")
                if record.authorization.valid_from and record.authorization.valid_to:
                    f.write(f"Valid: {record.authorization.valid_from} to {record.authorization.valid_to}\n")
                f.write("\n")
                
                if record.representative.name:
                    f.write("-" * 80 + "\n")
                    f.write("REPRESENTATIVE\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Name: {record.representative.name}\n")
                    if record.representative.id:
                        f.write(f"ID: {record.representative.id}\n")
                    f.write("\n")
                
                if record.documentation.required_documents:
                    f.write("-" * 80 + "\n")
                    f.write("DOCUMENTATION REQUIRED\n")
                    f.write("-" * 80 + "\n")
                    for doc in record.documentation.required_documents:
                        f.write(f"  • {doc}\n")
                    if record.documentation.submission_method:
                        f.write(f"Submit via: {record.documentation.submission_method}\n")
                    if record.documentation.fax_number:
                        f.write(f"Fax: {record.documentation.fax_number}\n")
                    if record.documentation.submission_deadline:
                        f.write(f"⚠️  Deadline: {record.documentation.submission_deadline}\n")
                    f.write("\n")
                
                if record.next_steps:
                    f.write("-" * 80 + "\n")
                    f.write("NEXT STEPS\n")
                    f.write("-" * 80 + "\n")
                    for i, step in enumerate(record.next_steps, 1):
                        f.write(f"{i}. {step}\n")
                    f.write("\n")
                
                if record.missing_fields:
                    f.write("-" * 80 + "\n")
                    f.write("⚠️  MISSING INFORMATION\n")
                    f.write("-" * 80 + "\n")
                    for field in record.missing_fields:
                        f.write(f"  • {field}\n")
                    f.write("\n")
                
                if record.validation_errors:
                    f.write("-" * 80 + "\n")
                    f.write("❌ VALIDATION ERRORS\n")
                    f.write("-" * 80 + "\n")
                    for error in record.validation_errors:
                        f.write(f"  • {error}\n")
                    f.write("\n")
                
                if record.validation_warnings:
                    f.write("-" * 80 + "\n")
                    f.write("⚠️  WARNINGS\n")
                    f.write("-" * 80 + "\n")
                    for warning in record.validation_warnings:
                        f.write(f"  • {warning}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
            
            logger.info(f"Saved summary to: {summary_filepath}")
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
    
    def load_record(self, filepath: str) -> PriorAuthRecord:
        """
        Load prior authorization record from file
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            PriorAuthRecord
        """
        try:
            return PriorAuthRecord.from_json_file(filepath)
        except Exception as e:
            logger.error(f"Error loading prior auth record from {filepath}: {e}")
            raise
    
    def list_records(
        self,
        status: Optional[AuthorizationStatus] = None,
        outcome: Optional[CallOutcome] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[str]:
        """
        List stored prior auth records with optional filters
        
        Args:
            status: Filter by authorization status
            outcome: Filter by call outcome
            start_date: Filter records from this date
            end_date: Filter records until this date
        
        Returns:
            List of file paths matching filters
        """
        records = []
        
        # Determine which subdirectories to search
        if status:
            subdirs = [self._get_subdir_for_status(status)]
        else:
            subdirs = ["approved", "pending", "denied", "failed"]
        
        # Search subdirectories
        for subdir in subdirs:
            subdir_path = self.storage_dir / subdir
            if not subdir_path.exists():
                continue
            
            for filepath in subdir_path.glob("*.json"):
                # Apply date filters if provided
                if start_date or end_date:
                    # Extract date from filename (YYYYMMDD_HHMMSS_CallID.json)
                    try:
                        date_str = filepath.stem.split('_')[0]
                        file_date = datetime.strptime(date_str, "%Y%m%d").date()
                        
                        if start_date and file_date < start_date:
                            continue
                        if end_date and file_date > end_date:
                            continue
                    except (ValueError, IndexError):
                        pass
                
                records.append(str(filepath))
        
        return sorted(records, reverse=True)  # Most recent first
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all stored records
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_records': 0,
            'by_status': {
                'approved': 0,
                'pending': 0,
                'denied': 0,
                'failed': 0
            },
            'by_outcome': {
                'success': 0,
                'partial': 0,
                'failed': 0,
                'disconnected': 0
            },
            'recent_calls': []
        }
        
        # Count records in each subdirectory
        for status_dir in ['approved', 'pending', 'denied', 'failed']:
            subdir = self.storage_dir / status_dir
            if subdir.exists():
                count = len(list(subdir.glob("*.json")))
                stats['by_status'][status_dir] = count
                stats['total_records'] += count
        
        # Get recent calls (last 10)
        all_records = self.list_records()
        for filepath in all_records[:10]:
            try:
                record = self.load_record(filepath)
                stats['recent_calls'].append({
                    'call_id': record.call_id,
                    'date': record.call_date.isoformat(),
                    'status': record.authorization.status.value,
                    'outcome': record.call_outcome.value,
                    'patient': record.patient.name
                })
            except Exception as e:
                logger.error(f"Error loading record for stats: {e}")
        
        return stats
    
    def _get_subdir_for_status(self, status: AuthorizationStatus) -> str:
        """Get subdirectory name for authorization status"""
        if status == AuthorizationStatus.APPROVED:
            return "approved"
        elif status == AuthorizationStatus.DENIED:
            return "denied"
        elif status in [AuthorizationStatus.PENDING, AuthorizationStatus.PEER_TO_PEER_REQUIRED, 
                       AuthorizationStatus.ADDITIONAL_INFO_REQUIRED]:
            return "pending"
        else:
            return "failed"
    
    def export_to_csv(self, output_file: str, records: Optional[List[str]] = None):
        """
        Export records to CSV format
        
        Args:
            output_file: Path to output CSV file
            records: Optional list of record filepaths to export (default: all)
        """
        import csv
        
        if records is None:
            records = self.list_records()
        
        if not records:
            logger.warning("No records to export")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'call_id', 'call_date', 'insurance_company',
                    'patient_name', 'patient_dob', 'member_id',
                    'provider_name', 'provider_npi',
                    'cpt_code', 'procedure_description', 'icd_code',
                    'authorization_status', 'authorization_number', 'reference_number',
                    'representative_name', 'call_outcome',
                    'missing_fields', 'validation_errors'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for filepath in records:
                    try:
                        record = self.load_record(filepath)
                        writer.writerow({
                            'call_id': record.call_id,
                            'call_date': record.call_date.isoformat(),
                            'insurance_company': record.insurance_company,
                            'patient_name': record.patient.name,
                            'patient_dob': record.patient.date_of_birth.isoformat() if record.patient.date_of_birth else '',
                            'member_id': record.patient.member_id or '',
                            'provider_name': record.provider.name,
                            'provider_npi': record.provider.npi or '',
                            'cpt_code': record.procedure.cpt_code,
                            'procedure_description': record.procedure.description or '',
                            'icd_code': record.procedure.icd_code or '',
                            'authorization_status': record.authorization.status.value,
                            'authorization_number': record.authorization.authorization_number or '',
                            'reference_number': record.authorization.reference_number or '',
                            'representative_name': record.representative.name or '',
                            'call_outcome': record.call_outcome.value,
                            'missing_fields': '; '.join(record.missing_fields),
                            'validation_errors': '; '.join(record.validation_errors)
                        })
                    except Exception as e:
                        logger.error(f"Error exporting record {filepath}: {e}")
            
            logger.info(f"Exported {len(records)} records to {output_file}")
            
        except Exception as e:
            logger.error(f"Error creating CSV export: {e}")
            raise


# Singleton instance
_storage_instance = None

def get_storage(storage_dir: str = "prior_auth_records") -> PriorAuthStorage:
    """Get singleton storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = PriorAuthStorage(storage_dir)
    return _storage_instance

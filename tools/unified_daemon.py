"""
Unified autonomous daemon integrating all Phase 3 components:
- Continuous ingestion and processing
- Prompt optimization
- Research hypothesis generation
- Retrospective validation
"""

import os
import sys
import time
import signal
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon import WikiDaemon
from prompt_optimizer import PromptOptimizer
from research_agent import ResearchAgent
from retrospective_validator import RetrospectiveValidator
from paper_agent import PaperAgent
from common import write_log


class UnifiedDaemon:
    """Unified autonomous system integrating all components."""
    
    def __init__(self):
        print("=" * 60)
        print("  LLM Wiki Unified Autonomous System")
        print("  Phase 3: Complete Integration")
        print("=" * 60)
        print()
        
        # Initialize all components
        print("🚀 Initializing components...")
        self.wiki_daemon = WikiDaemon()
        self.prompt_optimizer = None  # Lazy init
        self.research_agent = None  # Lazy init
        self.validator = None  # Lazy init
        self.paper_agent = None  # Lazy init
        
        # Scheduling
        self.last_optimization = 0
        self.last_research = 0
        self.last_validation = 0
        self.last_paper_generation = 0
        
        # Intervals (in seconds)
        self.optimization_interval = 3600 * 4  # 4 hours
        self.research_interval = 3600 * 6  # 6 hours
        self.validation_interval = 3600 * 24 * 7  # 7 days
        self.paper_interval = 3600 * 24 * 14  # 14 days (bi-weekly)
        
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        print("✓ All components initialized")
        print()
        print("Schedule:")
        print(f"  - Continuous: Source processing (daemon)")
        print(f"  - Every 4h: Prompt optimization")
        print(f"  - Every 6h: Research hypothesis generation")
        print(f"  - Every 7d: Retrospective validation")
        print(f"  - Every 14d: Research paper generation")
        print()
        
        write_log('unified_daemon', 'started', 'All components initialized')
    
    def shutdown(self, signum, frame):
        """Graceful shutdown."""
        print("\n🛑 Shutdown signal received...")
        self.running = False
        self.wiki_daemon.running = False
        
        if self.prompt_optimizer:
            self.prompt_optimizer.close()
        if self.research_agent:
            self.research_agent.close()
        if self.validator:
            self.validator.close()
        if self.paper_agent:
            self.paper_agent.close()
        
        write_log('unified_daemon', 'shutdown', 'Graceful shutdown complete')
    
    def run(self):
        """Main unified loop."""
        print("🤖 Unified daemon started\n")
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                current_time = time.time()
                
                print(f"\n{'='*60}")
                print(f"  Cycle #{cycle_count} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"{'='*60}\n")
                
                # 1. Process sources (continuous)
                print("📥 Processing sources...")
                self.process_sources()
                
                # 2. Prompt optimization (every 4 hours)
                if current_time - self.last_optimization > self.optimization_interval:
                    print("\n🔬 Running prompt optimization...")
                    self.run_optimization()
                    self.last_optimization = current_time
                
                # 3. Research hypotheses (every 6 hours)
                if current_time - self.last_research > self.research_interval:
                    print("\n💡 Generating research hypotheses...")
                    self.run_research()
                    self.last_research = current_time
                
                # 4. Retrospective validation (every 7 days)
                if current_time - self.last_validation > self.validation_interval:
                    print("\n🔍 Running retrospective validation...")
                    self.run_validation()
                    self.last_validation = current_time
                
                # 5. Research paper generation (every 14 days)
                if current_time - self.last_paper_generation > self.paper_interval:
                    print("\n📝 Generating research paper...")
                    self.run_paper_generation()
                    self.last_paper_generation = current_time
                
                # 6. Status report
                self.print_status()
                
                # 7. Sleep
                if self.wiki_daemon.queue.empty():
                    print(f"\n💤 Sleeping for 5 minutes...")
                    time.sleep(300)  # 5 minutes
                else:
                    time.sleep(10)  # Quick cycle if queue has items
                    
            except KeyboardInterrupt:
                self.shutdown(None, None)
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                write_log('unified_daemon_error', 'main_loop', str(e))
                time.sleep(60)  # Wait before retry
        
        print("\n👋 Unified daemon stopped")
    
    def process_sources(self):
        """Process sources from queue."""
        # Poll monitors
        self.wiki_daemon.poll_monitors()
        
        # Process up to 10 sources
        processed = 0
        while not self.wiki_daemon.queue.empty() and processed < 10:
            priority, source_path = self.wiki_daemon.queue.get()
            self.wiki_daemon.process_source(source_path, priority)
            processed += 1
        
        if processed > 0:
            print(f"   ✓ Processed {processed} sources")
        else:
            print(f"   No sources in queue")
    
    def run_optimization(self):
        """Run prompt optimization cycle."""
        try:
            if not self.prompt_optimizer:
                self.prompt_optimizer = PromptOptimizer()
            
            # Run 1 optimization cycle
            kept = self.prompt_optimizer.run_optimization_cycle()
            
            if kept:
                print(f"   ✓ Optimization kept (improvement found)")
            else:
                print(f"   ✗ Optimization reverted (no improvement)")
                
        except Exception as e:
            print(f"   ❌ Optimization error: {e}")
            write_log('unified_daemon_error', 'optimization', str(e))
    
    def run_research(self):
        """Run research hypothesis generation."""
        try:
            if not self.research_agent:
                self.research_agent = ResearchAgent()
            
            # Generate hypotheses
            hypotheses = self.research_agent.generate_daily_hypotheses()
            
            # Execute top 2 hypotheses
            executed = 0
            for hypothesis in hypotheses[:2]:
                result = self.research_agent.execute_hypothesis(hypothesis)
                if result['decision'] == 'SUCCESS':
                    executed += 1
            
            print(f"   ✓ Generated {len(hypotheses)} hypotheses, executed {executed}")
            
        except Exception as e:
            print(f"   ❌ Research error: {e}")
            write_log('unified_daemon_error', 'research', str(e))
    
    def run_validation(self):
        """Run retrospective validation."""
        try:
            if not self.validator:
                self.validator = RetrospectiveValidator(lookback_days=7)
            
            self.validator.run_weekly_validation()
            
            print(f"   ✓ Validated {self.validator.pages_validated} pages")
            print(f"   ✓ Found {self.validator.contradictions_found} contradictions")
            print(f"   ✓ Adjusted {self.validator.confidence_adjustments} confidence scores")
            
        except Exception as e:
            print(f"   ❌ Validation error: {e}")
            write_log('unified_daemon_error', 'validation', str(e))
    
    def run_paper_generation(self):
        """Run research paper generation."""
        try:
            if not self.paper_agent:
                self.paper_agent = PaperAgent()
            
            # Generate 1 paper with combined topics
            paper = self.paper_agent.generate_paper(combine_topics=True)
            
            print(f"   ✓ Generated paper: {paper['title']}")
            print(f"   ✓ Topics: {', '.join(paper['topics'])}")
            print(f"   ✓ Word count: {paper['word_count']}")
            print(f"   ✓ Saved to: {paper['filename']}")
            
        except Exception as e:
            print(f"   ❌ Paper generation error: {e}")
            write_log('unified_daemon_error', 'paper_generation', str(e))
    
    def print_status(self):
        """Print system status."""
        print(f"\n📊 System Status:")
        print(f"   Sources processed: {self.wiki_daemon.processed_count}")
        print(f"   Failures: {self.wiki_daemon.failure_count}")
        print(f"   Queue size: {self.wiki_daemon.queue.qsize()}")
        
        if self.wiki_daemon.processed_count + self.wiki_daemon.failure_count > 0:
            success_rate = (self.wiki_daemon.processed_count / 
                          (self.wiki_daemon.processed_count + self.wiki_daemon.failure_count) * 100)
            print(f"   Success rate: {success_rate:.1f}%")
        
        # Time until next scheduled tasks
        current_time = time.time()
        
        next_opt = max(0, self.optimization_interval - (current_time - self.last_optimization))
        next_res = max(0, self.research_interval - (current_time - self.last_research))
        next_val = max(0, self.validation_interval - (current_time - self.last_validation))
        next_paper = max(0, self.paper_interval - (current_time - self.last_paper_generation))
        
        print(f"\n⏰ Next scheduled tasks:")
        print(f"   Optimization: {next_opt/3600:.1f}h")
        print(f"   Research: {next_res/3600:.1f}h")
        print(f"   Validation: {next_val/3600/24:.1f}d")
        print(f"   Paper generation: {next_paper/3600/24:.1f}d")


def main():
    """Entry point for unified daemon."""
    daemon = UnifiedDaemon()
    daemon.run()


if __name__ == '__main__':
    main()

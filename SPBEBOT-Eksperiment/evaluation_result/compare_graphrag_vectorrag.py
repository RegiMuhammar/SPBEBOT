#!/usr/bin/env python3
"""
Script to compare GraphRAG and VectorRAG evaluation results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_results():
    """
    Load evaluation results from both GraphRAG and VectorRAG
    """
    try:
        # Load GraphRAG results
        graphrag_results = pd.read_csv("evaluation_spbe_graphrag.csv")
        print("✅ Loaded GraphRAG results")
        
        # Load VectorRAG results
        vector_results = pd.read_csv("evaluation2_spbe_vector.csv")
        print("✅ Loaded VectorRAG results")
        
        return graphrag_results, vector_results
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return None, None

def calculate_metrics_summary(graphrag_results, vector_results):
    """
    Calculate summary metrics for comparison
    """
    if graphrag_results is None or vector_results is None:
        return None
    
    # Calculate averages for each metric
    metrics = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']
    
    summary = {}
    for metric in metrics:
        if metric in graphrag_results.columns and metric in vector_results.columns:
            summary[f'graphrag_{metric}_mean'] = graphrag_results[metric].mean()
            summary[f'vector_{metric}_mean'] = vector_results[metric].mean()
            summary[f'{metric}_difference'] = summary[f'graphrag_{metric}_mean'] - summary[f'vector_{metric}_mean']
    
    return summary

def create_comparison_visualization(graphrag_results, vector_results):
    """
    Create visualization comparing GraphRAG vs VectorRAG
    """
    if graphrag_results is None or vector_results is None:
        return
    
    # Prepare data for plotting
    metrics = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']
    
    # Create comparison data
    comparison_data = []
    for metric in metrics:
        if metric in graphrag_results.columns and metric in vector_results.columns:
            # GraphRAG values
            for value in graphrag_results[metric]:
                comparison_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': value,
                    'Method': 'GraphRAG'
                })
            
            # VectorRAG values
            for value in vector_results[metric]:
                comparison_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': value,
                    'Method': 'VectorRAG'
                })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Box plot
    plt.subplot(2, 2, 1)
    sns.boxplot(data=df_comparison, x='Metric', y='Value', hue='Method')
    plt.title('Metric Comparison: GraphRAG vs VectorRAG')
    plt.xticks(rotation=45)
    plt.legend()
    
    # Bar plot of means
    plt.subplot(2, 2, 2)
    summary = calculate_metrics_summary(graphrag_results, vector_results)
    if summary:
        metrics_names = [m.replace('_', ' ').title() for m in metrics]
        graphrag_means = [summary[f'graphrag_{m}_mean'] for m in metrics]
        vector_means = [summary[f'vector_{m}_mean'] for m in metrics]
        
        x = np.arange(len(metrics_names))
        width = 0.35
        
        plt.bar(x - width/2, graphrag_means, width, label='GraphRAG', alpha=0.8)
        plt.bar(x + width/2, vector_means, width, label='VectorRAG', alpha=0.8)
        
        plt.xlabel('Metrics')
        plt.ylabel('Average Score')
        plt.title('Average Metric Scores')
        plt.xticks(x, metrics_names, rotation=45)
        plt.legend()
    
    # Difference plot
    plt.subplot(2, 2, 3)
    if summary:
        differences = [summary[f'{m}_difference'] for m in metrics]
        colors = ['green' if d > 0 else 'red' for d in differences]
        
        plt.bar(metrics_names, differences, color=colors, alpha=0.7)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xlabel('Metrics')
        plt.ylabel('Difference (GraphRAG - VectorRAG)')
        plt.title('Performance Difference')
        plt.xticks(rotation=45)
    
    # Heatmap of individual scores
    plt.subplot(2, 2, 4)
    pivot_data = df_comparison.pivot_table(
        values='Value', 
        index=df_comparison.groupby('Method').cumcount(), 
        columns=['Method', 'Metric'], 
        aggfunc='mean'
    )
    
    if not pivot_data.empty:
        sns.heatmap(pivot_data.T, annot=True, cmap='RdYlBu_r', center=0.5)
        plt.title('Individual Question Scores Heatmap')
    
    plt.tight_layout()
    plt.savefig('graphrag_vs_vectorrag_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_detailed_comparison(graphrag_results, vector_results):
    """
    Print detailed comparison of results
    """
    if graphrag_results is None or vector_results is None:
        return
    
    print("\n" + "="*60)
    print("📊 DETAILED COMPARISON: GraphRAG vs VectorRAG")
    print("="*60)
    
    metrics = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']
    
    for metric in metrics:
        if metric in graphrag_results.columns and metric in vector_results.columns:
            print(f"\n🔍 {metric.replace('_', ' ').title()}:")
            print(f"   GraphRAG: {graphrag_results[metric].mean():.3f} ± {graphrag_results[metric].std():.3f}")
            print(f"   VectorRAG: {vector_results[metric].mean():.3f} ± {vector_results[metric].std():.3f}")
            
            diff = graphrag_results[metric].mean() - vector_results[metric].mean()
            if diff > 0:
                print(f"   📈 GraphRAG performs better by {diff:.3f}")
            elif diff < 0:
                print(f"   📉 VectorRAG performs better by {abs(diff):.3f}")
            else:
                print(f"   ⚖️  Both methods perform equally")
    
    # Overall performance
    print(f"\n🎯 OVERALL PERFORMANCE:")
    graphrag_overall = np.mean([graphrag_results[m].mean() for m in metrics if m in graphrag_results.columns])
    vector_overall = np.mean([vector_results[m].mean() for m in metrics if m in vector_results.columns])
    
    print(f"   GraphRAG Overall: {graphrag_overall:.3f}")
    print(f"   VectorRAG Overall: {vector_overall:.3f}")
    
    if graphrag_overall > vector_overall:
        print(f"   🏆 GraphRAG performs better overall")
    elif vector_overall > graphrag_overall:
        print(f"   🏆 VectorRAG performs better overall")
    else:
        print(f"   🤝 Both methods perform equally overall")

def save_comparison_report(graphrag_results, vector_results):
    """
    Save detailed comparison report
    """
    if graphrag_results is None or vector_results is None:
        return
    
    summary = calculate_metrics_summary(graphrag_results, vector_results)
    if not summary:
        return
    
    # Create comparison dataframe
    metrics = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']
    comparison_data = []
    
    for metric in metrics:
        if metric in graphrag_results.columns and metric in vector_results.columns:
            comparison_data.append({
                'Metric': metric.replace('_', ' ').title(),
                'GraphRAG_Mean': graphrag_results[metric].mean(),
                'GraphRAG_Std': graphrag_results[metric].std(),
                'VectorRAG_Mean': vector_results[metric].mean(),
                'VectorRAG_Std': vector_results[metric].std(),
                'Difference': summary[f'{metric}_difference'],
                'Better_Method': 'GraphRAG' if summary[f'{metric}_difference'] > 0 else 'VectorRAG'
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv('graphrag_vs_vectorrag_comparison.csv', index=False)
    print("✅ Comparison report saved to 'graphrag_vs_vectorrag_comparison.csv'")

def main():
    """
    Main function to run comparison
    """
    print("🔍 Starting GraphRAG vs VectorRAG Comparison...")
    print("="*50)
    
    # Load results
    graphrag_results, vector_results = load_results()
    
    if graphrag_results is None or vector_results is None:
        print("❌ Cannot proceed without both result files")
        return
    
    # Print detailed comparison
    print_detailed_comparison(graphrag_results, vector_results)
    
    # Create visualization
    print("\n📊 Creating visualization...")
    create_comparison_visualization(graphrag_results, vector_results)
    
    # Save comparison report
    print("\n💾 Saving comparison report...")
    save_comparison_report(graphrag_results, vector_results)
    
    print("\n✅ Comparison completed successfully!")
    print("📁 Generated files:")
    print("   - graphrag_vs_vectorrag_comparison.png")
    print("   - graphrag_vs_vectorrag_comparison.csv")

if __name__ == "__main__":
    main() 
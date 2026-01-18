import argparse
from config.settings import settings
from workflows.graph import run_workflow, visualize_workflow

def main():
    """Main entry point"""
    
    # Validate configuration
    settings.validate()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Content Research & Writing Assistant"
    )
    parser.add_argument(
        "topic",
        help="Topic to research and write about"
    )
    parser.add_argument(
        "--type",
        default="blog",
        choices=["blog", "article", "social"],
        help="Type of content to generate (default: blog)"
    )
    parser.add_argument(
        "--audience",
        default=None,
        help="Target audience for the content"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Visualize the workflow graph"
    )
    
    args = parser.parse_args()
    
    # Visualize graph if requested
    if args.visualize:
        visualize_workflow()
        return
    
    # Run workflow
    run_workflow(
        topic=args.topic,
        content_type=args.type,
        target_audience=args.audience
    )


if __name__ == "__main__":
    main()